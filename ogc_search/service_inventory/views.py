from django.conf import settings
from django.shortcuts import render
from django.views.generic import View
import logging
from math import ceil
import pysolr
import re

logger = logging.getLogger('ogc_search')


def _convert_facet_list_to_dict(facet_list: list, reverse: bool = False) -> dict:
    """
    Solr returns search facet results in the form of an alternating list. Convert the list into a dictionary key
    on the facet
    :param facet_list: facet list returned by Solr
    :param reverse: boolean flag indicating if the search results should be returned in reverse order
    :return: A dictonary of the facet values and counts
    """
    facet_dict = {}
    for i in range(0, len(facet_list)):
        if i % 2 == 0:
            facet_dict[facet_list[i]] = facet_list[i + 1]
    if reverse:
        rkeys = sorted(facet_dict,  reverse=True)
        facet_dict_r = {}
        for k in rkeys:
            facet_dict_r[k] = facet_dict[k]
        return facet_dict_r
    else:
        return facet_dict


def _calc_pagination_range(results, pagesize, current_page):
    pages = int(ceil(results.hits / pagesize))
    delta = 2
    if current_page > pages:
        current_page = pages
    elif current_page < 1:
        current_page = 1
    left = current_page - delta
    right = current_page + delta + 1
    pagination = []
    spaced_pagination = []

    for p in range(1, pages + 1):
        if (p == 1) or (p == pages) or (left <= p < right):
            pagination.append(p)

    last = None
    for p in pagination:
        if last:
            if p - last == 2:
                spaced_pagination.append(last + 1)
            elif p - last != 1:
                spaced_pagination.append(0)
        spaced_pagination.append(p)
        last = p

    return spaced_pagination


class SISearchView(View):

    def __init__(self):
        super().__init__()

        items_per_page = int(settings.SI_ITEMS_PER_PAGE)

        # French search fields
        self.solr_fields_fr = ("id,service_id_s,service_name_fr_s,service_name_txt_fr,"
                               "service_description_fr_s,service_description_txt_fr,"
                               "new_service_id_s,"
                               "authority_fr_s,authority_txt_fr,"
                               "program_name_fr_s,program_name_txt_fr,"
                               "special_remarks_fr_s,special_remarks_txt_fr,"
                               "owner_org_fr_s,owner_org_title_txt_fr,"
                               "service_url_fr_s,program_id_code_s,online_applications_fr_s,"
                               "web_visits_info_service_fr_s,calls_received_fr_s,in_person_applications_fr_s,"
                               "email_applications_fr_s,fax_applications_fr_s,postal_mail_applications_fr_s,"
                               "fiscal_year_s,external_internal_fr_s,"
                               "service_type_fr_s,special_designations_fr_s,client_target_groups_fr_s,"
                               "service_fee_fr_s,cra_business_number_fr_s,use_of_sin_fr_s,e_registration_fr_s,"
                               "e_authentication_fr_s,e_decision_fr_s,e_issuance_fr_s,e_feedback_fr_s,"
                               "client_feedback_fr_s,"
                               "standards")

        self.solr_query_fields_fr = ['service_name_txt_fr^5', 'service_description_txt_fr^3', 'authority_txt_fr^2',
                                     'program_name_txt_fr^3', 'special_remarks_txt_fr^6', 'owner_org_title_txt_fr^2',
                                     '_text_fr_^0.5']

        self.solr_facet_fields_fr = ['{!ex=tag_owner_org_fr_s}owner_org_fr_s',
                                     '{!ex=tag_fiscal_year_s}fiscal_year_s',
                                     '{!ex=tag_external_internal_fr_s}external_internal_fr_s',
                                     '{!ex=tag_service_type_fr_s}service_type_fr_s',
                                     '{!ex=tag_special_designations_fr_s}special_designations_fr_s',
                                     '{!ex=tag_client_target_groups_fr_s}client_target_groups_fr_s',
                                     '{!ex=tag_service_fee_fr_s}service_fee_fr_s',
                                     '{!ex=tag_cra_business_number_fr_s}cra_business_number_fr_s',
                                     '{!ex=tag_e_registration_fr_s}e_registration_fr_s',
                                     '{!ex=tag_e_authentication_fr_s}e_authentication_fr_s',
                                     '{!ex=tag_e_decision_fr_s}e_decision_fr_s',
                                     '{!ex=tag_e_issuance_fr_s}e_issuance_fr_s',
                                     '{!ex=tag_e_feedback_fr_s}e_feedback_fr_s',
                                     '{!ex=tag_client_feedback_fr_s}client_feedback_fr_s']

        self.solr_hl_fields_fr = ['service_name_txt_fr', 'service_description_txt_fr', 'authority_txt_fr',
                                  'program_name_txt_fr', 'special_remarks_txt_fr', 'owner_org_title_txt_fr']

        self.phrase_xtras_fr = {
            'hl': 'on',
            'hl.simple.pre': '<mark class="highlight">',
            'hl.simple.post': '</mark>',
            'hl.method': 'unified',
            'hl.snippets': items_per_page,
            'hl.fl': self.solr_hl_fields_fr,
            'hl.preserveMulti': 'true',
            'ps': items_per_page,
            'mm': '3<70%',
        }

        # English search fields
        self.solr_fields_en = ("id,service_id_s,service_name_en_s,service_name_txt_en,"
                               "service_description_en_s,service_description_txt_en,"
                               "new_service_id_s,"
                               "authority_en_s,authority_txt_en,"
                               "program_name_en_s,program_name_txt_en,"
                               "special_remarks_en_s,special_remarks_txt_en,"
                               "owner_org_en_s,owner_org_title_txt_en,"
                               "service_url_en_s,program_id_code_s,online_applications_en_s,"
                               "web_visits_info_service_en_s,calls_received_en_s,in_person_applications_en_s,"
                               "email_applications_en_s,fax_applications_en_s,postal_mail_applications_en_s,"
                               "fiscal_year_s,external_internal_en_s,"
                               "service_type_en_s,special_designations_en_s,client_target_groups_en_s,"
                               "service_fee_en_s,cra_business_number_en_s,use_of_sin_en_s,e_registration_en_s,"
                               "e_authentication_en_s,e_decision_en_s,e_issuance_en_s,e_feedback_en_s,"
                               "client_feedback_en_s,"
                               "standards")

        self.solr_query_fields_en = ['service_name_txt_en^5', 'service_description_txt_en^3', 'authority_txt_en^2',
                                     'program_name_txt_en^3', 'special_remarks_txt_en^6', 'owner_org_title_txt_en^2',
                                     '_text_en_^0.5']

        self.solr_facet_fields_en = ['{!ex=tag_owner_org_en_s}owner_org_en_s',
                                     '{!ex=tag_fiscal_year_s}fiscal_year_s',
                                     '{!ex=tag_external_internal_en_s}external_internal_en_s',
                                     '{!ex=tag_service_type_en_s}service_type_en_s',
                                     '{!ex=tag_special_designations_en_s}special_designations_en_s',
                                     '{!ex=tag_client_target_groups_en_s}client_target_groups_en_s',
                                     '{!ex=tag_service_fee_en_s}service_fee_en_s',
                                     '{!ex=tag_cra_business_number_en_s}cra_business_number_en_s',
                                     '{!ex=tag_e_registration_en_s}e_registration_en_s',
                                     '{!ex=tag_e_authentication_en_s}e_authentication_en_s',
                                     '{!ex=tag_e_decision_en_s}e_decision_en_s',
                                     '{!ex=tag_e_issuance_en_s}e_issuance_en_s',
                                     '{!ex=tag_e_feedback_en_s}e_feedback_en_s',
                                     '{!ex=tag_client_feedback_en_s}client_feedback_en_s']

        self.solr_hl_fields_en = ['service_name_txt_en', 'service_description_txt_en', 'authority_txt_en',
                                  'program_name_txt_en', 'special_remarks_txt_en', 'owner_org_title_txt_en']

        self.phrase_xtras_en = {
            'hl': 'on',
            'hl.simple.pre': '<mark class="highlight">',
            'hl.simple.post': '</mark>',
            'hl.method': 'unified',
            'hl.snippets': items_per_page,
            'hl.fl': self.solr_hl_fields_en,
            'hl.preserveMulti': 'true',
            'ps': items_per_page,
            'mm': '3<70%',
        }

    @staticmethod
    def split_with_quotes(csv_string):
        # As per https://stackoverflow.com/a/23155180
        return re.findall(r'[^"\s]\S*|".+?"', csv_string)

    def solr_query(self, q, start_row='0', pagesize='10', facets={}, language='en',
                   sort_order='score asc', ids=''):
        solr = pysolr.Solr(settings.SOLR_SI)
        solr_facets = []
        if language == 'fr':
            extras = {
                'start': start_row,
                'rows': pagesize,
                'facet': 'on',
                'facet.sort': 'index',
                'facet.field': self.solr_facet_fields_fr,
                'fq': solr_facets,
                'fl': self.solr_fields_fr,
                'defType': 'edismax',
                'qf': self.solr_query_fields_fr,
                'sort': sort_order,
            }

        else:
            extras = {
                'start': start_row,
                'rows': pagesize,
                'facet': 'on',
                'facet.sort': 'index',
                'facet.field': self.solr_facet_fields_en,
                'fq': solr_facets,
                'fl': self.solr_fields_en,
                'defType': 'edismax',
                'qf': self.solr_query_fields_en,
                'sort': sort_order,
            }

        for facet in facets.keys():
            if facets[facet] != '':
                facet_terms = facets[facet].split('|')
                quoted_terms = ['"{0}"'.format(item) for item in facet_terms]
                facet_text = '{{!tag=tag_{0}}}{0}:({1})'.format(facet, ' OR '.join(quoted_terms))
                solr_facets.append(facet_text)

        if q != '*':
            if language == 'fr':
                extras.update(self.phrase_xtras_fr)
            elif language == 'en':
                extras.update(self.phrase_xtras_en)

        sr = solr.search(q, **extras)

        # If there are highlighted results, substitute the highlighted field in the doc results

        for doc in sr.docs:
            if doc['id'] in sr.highlighting:
                hl_entry = sr.highlighting[doc['id']]
                for hl_fld_id in hl_entry:
                    if hl_fld_id in doc and len(hl_entry[hl_fld_id]) > 0:
                        if type(doc[hl_fld_id]) is list:
                            # Scan Multi-valued Solr fields for matching highlight fields
                            for y in hl_entry[hl_fld_id]:
                                y_filtered = re.sub('</mark>', '', re.sub(r'<mark class="highlight">', "", y))
                                x = 0
                                for hl_fld_txt in doc[hl_fld_id]:
                                    if hl_fld_txt == y_filtered:
                                        doc[hl_fld_id][x] = y
                                    x += 1
                        else:
                            # Straight-forward field replacement with highlighted text
                            doc[hl_fld_id] = hl_entry[hl_fld_id][0]

        return sr

    def get(self, request):

        context = dict(LANGUAGE_CODE=request.LANGUAGE_CODE, )
        context["cdts_version"] = settings.CDTS_VERSION
        context["od_en_url"] = settings.OPEN_DATA_EN_URL_BASE
        context["od_fr_url"] = settings.OPEN_DATA_FR_URL_BASE
        context["si_ds_id"] = settings.SI_DATASET_ID
        context["si_ds_title_en"] = settings.SI_DATASET_TITLE_EN
        context["si_ds_title_fr"] = settings.SI_DATASET_TITLE_FR
        context["si_dv_path"] = settings.SI_DATAVIZ_PATH

        # Get any search terms

        search_text = str(request.GET.get('search_text', ''))
        # Respect quoted strings
        context['search_text'] = search_text
        search_terms = self.split_with_quotes(search_text)
        if len(search_terms) == 0:
            solr_search_terms = "*"
        elif len(search_terms) == 1:
            solr_search_terms = '"{0}"'.format(search_terms)
        else:
            solr_search_terms = ' '.join(search_terms)

        items_per_page = int(settings.SI_ITEMS_PER_PAGE)

        # Retrieve search results and transform facets results to python dict

        solr_search_orgs: str = request.GET.get('si-search-orgs', '')
        solr_search_years: str = request.GET.get('si-search-year', '')
        solr_search_xis: str = request.GET.get('si-search-ext-int', '')
        solr_search_stype: str = request.GET.get('si-search-service-type', '')
        solr_search_designations: str = request.GET.get('si-search-designations', '')
        solr_search_targets: str = request.GET.get('si-search-target-groups', '')
        solr_search_fees: str = request.GET.get('si-search-service-fee', '')
        solr_search_cra_no: str = request.GET.get('si-search-cra-number', '')
        solr_search_e_reg: str = request.GET.get('si-search-e-reg', '')
        solr_search_e_authenticate: str = request.GET.get('si-search-e-authenticate', '')
        solr_search_e_decision: str = request.GET.get('si-search-e-decision', '')
        solr_search_e_issuance: str = request.GET.get('si-search-e-issuance', '')
        solr_search_e_feedback: str = request.GET.get('si-search-e-feedback', '')

        context["organizations_selected"] = solr_search_orgs
        context["organizations_selected_list"] = solr_search_orgs.split('|')
        context["years_selected"] = solr_search_years
        context["years_selected_list"] = solr_search_years.split('|')
        context["xis_selected"] = solr_search_xis
        context["xis_selected_list"] = solr_search_xis.split('|')
        context["stypes_selected"] = solr_search_stype
        context["stypes_selected_list"] = solr_search_stype.split('|')
        context["designations_selected"] = solr_search_designations
        context["designations_selected_list"] = solr_search_designations.split('|')
        context["targets_selected"] = solr_search_targets
        context["targets_selected_list"] = solr_search_targets.split('|')
        context["fees_selected"] = solr_search_fees
        context["fees_selected_list"] = solr_search_fees.split('|')
        context["cra_no_selected"] = solr_search_cra_no
        context["cra_no_selected_list"] = solr_search_cra_no.split('|')
        context["e_reg_selected"] = solr_search_e_reg
        context["e_reg_selected_list"] = solr_search_e_reg.split('|')
        context["e_authenticate_selected"] = solr_search_e_authenticate
        context["e_authenticate_selected_list"] = solr_search_e_authenticate.split('|')
        context["e_decision_selected"] = solr_search_e_decision
        context["e_decision_selected_list"] = solr_search_e_decision.split('|')
        context["e_issuance_selected"] = solr_search_e_issuance
        context["e_issuance_selected_list"] = solr_search_e_issuance.split('|')
        context["e_feedback_selected"] = solr_search_e_feedback
        context["e_feedback_selected_list"] = solr_search_e_feedback.split('|')

        # Calculate a starting row for the Solr search results. We only retrieve one page at a time

        try:
            page = int(request.GET.get('page', 1))
        except ValueError:
            page = 1
        if page < 1:
            page = 1
        elif page > 10000:  # @magic_number: arbitrary upper range
            page = 10000
        start_row = items_per_page * (page - 1)

        solr_search_sort = request.GET.get('sort', 'score desc')
        if request.LANGUAGE_CODE == 'fr':
            if solr_search_sort not in ['score desc', 'program_name_fr_s asc', 'service_name_fr_s asc']:
                solr_search_sort = 'score desc'
        else:
            if solr_search_sort not in ['score desc', 'program_name_en_s asc', 'service_name_en_s asc']:
                solr_search_sort = 'score desc'
        context['sortby'] = solr_search_sort

        if request.LANGUAGE_CODE == 'fr':
            facets_dict = dict(owner_org_fr_s=context['organizations_selected'],
                               fiscal_year_s=context['years_selected'],
                               external_internal_fr_s=context['xis_selected'],
                               service_type_fr_s=context['stypes_selected'],
                               special_designations_fr_s=context['designations_selected'],
                               client_target_groups_fr_s=context['targets_selected'],
                               service_fee_fr_s=context["fees_selected"],
                               cra_business_number_fr_s=context["cra_no_selected"],
                               e_registration_fr_s=context["e_reg_selected"],
                               e_authentication_fr_s=context["e_authenticate_selected"],
                               e_decision_fr_s=context["e_decision_selected"],
                               e_issuance_fr_s=context["e_issuance_selected"],
                               e_feedback_fr_s=context["e_feedback_selected"],
                               )
        else:
            facets_dict = dict(owner_org_en_s=context['organizations_selected'],
                               fiscal_year_s=context['years_selected'],
                               external_internal_en_s=context['xis_selected'],
                               service_type_en_s=context['stypes_selected'],
                               special_designations_en_s=context['designations_selected'],
                               client_target_groups_en_s=context['targets_selected'],
                               service_fee_en_s=context["fees_selected"],
                               cra_business_number_en_s=context["cra_no_selected"],
                               e_registration_en_s=context["e_reg_selected"],
                               e_authentication_en_s=context["e_authenticate_selected"],
                               e_decision_en_s=context["e_decision_selected"],
                               e_issuance_en_s=context["e_issuance_selected"],
                               e_feedback_en_s=context["e_feedback_selected"],
                               )

        search_results = self.solr_query(solr_search_terms, start_row=str(start_row), pagesize=str(items_per_page), facets=facets_dict,
                                         language=request.LANGUAGE_CODE,
                                         sort_order=solr_search_sort)

        solr_search_orgs: str = request.GET.get('si-search-orgs', '')
        context["organizations_selected"] = solr_search_orgs

        context['results'] = search_results
        pagination = _calc_pagination_range(context['results'], items_per_page, page)
        context['pagination'] = pagination
        context['previous_page'] = (1 if page == 1 else page - 1)
        last_page = (pagination[len(pagination) - 1] if len(pagination) > 0 else 1)
        last_page = (1 if last_page < 1 else last_page)
        context['last_page'] = last_page
        next_page = page + 1
        next_page = (last_page if next_page > last_page else next_page)
        context['next_page'] = next_page
        context['currentpage'] = page

        if request.LANGUAGE_CODE == 'fr':
            context['org_facets_fr'] = _convert_facet_list_to_dict(
                search_results.facets['facet_fields']['owner_org_fr_s'])
            context['xis_facets_fr'] = _convert_facet_list_to_dict(
                search_results.facets['facet_fields']['external_internal_fr_s'])
            context['stype_facets_fr'] = _convert_facet_list_to_dict(
                search_results.facets['facet_fields']['service_type_fr_s'])
            context['designation_facets_fr'] = _convert_facet_list_to_dict(
                search_results.facets['facet_fields']['special_designations_fr_s'])
            context['targets_facets_fr'] = _convert_facet_list_to_dict(
                search_results.facets['facet_fields']['client_target_groups_fr_s'])
            context['fees_facets_fr'] = _convert_facet_list_to_dict(
                search_results.facets['facet_fields']['service_fee_fr_s'])
            context['cra_no_facets_fr'] = _convert_facet_list_to_dict(
                search_results.facets['facet_fields']['cra_business_number_fr_s'])
            context['e_reg_facets_fr'] = _convert_facet_list_to_dict(
                search_results.facets['facet_fields']['e_registration_fr_s'])
            context['e_authenticate_facets_fr'] = _convert_facet_list_to_dict(
                search_results.facets['facet_fields']['e_authentication_fr_s'])
            context['e_decision_facets_fr'] = _convert_facet_list_to_dict(
                search_results.facets['facet_fields']['e_decision_fr_s'])
            context['e_issuance_facets_fr'] = _convert_facet_list_to_dict(
                search_results.facets['facet_fields']['e_issuance_fr_s'])
            context['e_feedback_facets_fr'] = _convert_facet_list_to_dict(
                search_results.facets['facet_fields']['e_feedback_fr_s'])
        else:
            context['org_facets_en'] = _convert_facet_list_to_dict(
                search_results.facets['facet_fields']['owner_org_en_s'])
            context['xis_facets_en'] = _convert_facet_list_to_dict(
                search_results.facets['facet_fields']['external_internal_en_s'])
            context['stype_facets_en'] = _convert_facet_list_to_dict(
                search_results.facets['facet_fields']['service_type_en_s'])
            context['designation_facets_en'] = _convert_facet_list_to_dict(
                search_results.facets['facet_fields']['special_designations_en_s'])
            context['targets_facets_en'] = _convert_facet_list_to_dict(
                search_results.facets['facet_fields']['client_target_groups_en_s'])
            context['fees_facets_en'] = _convert_facet_list_to_dict(
                search_results.facets['facet_fields']['service_fee_en_s'])
            context['cra_no_facets_en'] = _convert_facet_list_to_dict(
                search_results.facets['facet_fields']['cra_business_number_en_s'])
            context['e_reg_facets_en'] = _convert_facet_list_to_dict(
                search_results.facets['facet_fields']['e_registration_en_s'])
            context['e_authenticate_facets_en'] = _convert_facet_list_to_dict(
                search_results.facets['facet_fields']['e_authentication_en_s'])
            context['e_decision_facets_en'] = _convert_facet_list_to_dict(
                search_results.facets['facet_fields']['e_decision_en_s'])
            context['e_issuance_facets_en'] = _convert_facet_list_to_dict(
                search_results.facets['facet_fields']['e_issuance_en_s'])
            context['e_feedback_facets_en'] = _convert_facet_list_to_dict(
                search_results.facets['facet_fields']['e_feedback_en_s'])

        context['fiscal_year'] = _convert_facet_list_to_dict(
            search_results.facets['facet_fields']['fiscal_year_s'])

        return render(request, "si_search.html", context)