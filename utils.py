import logging
import requests
from typing import Optional
import unicodedata, re


from cpr_sdk.embedding import Embedder
from cpr_sdk.exceptions import DocumentNotFoundError, FetchError, QueryError
from cpr_sdk.models.search import Hit, SearchParameters, SearchResponse, Family, Document, Passage
from cpr_sdk.search_adaptors import SearchAdapter
from cpr_sdk.vespa import split_document_id


LOGGER = logging.getLogger(__name__)

def flatten_list(nested_list):
    flat_list = []
    for element in nested_list:
        if isinstance(element, list):
            flat_list.extend(flatten_list(element))
        else:
            flat_list.append(element)
    return flat_list

def slugify(value):
    """
    Converts to lowercase, removes non-word characters (alphanumerics and
    underscores) and converts spaces to hyphens. Also strips leading and
    trailing whitespace.
    """
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub('[^\w\s-]', '', value).strip().lower()
    return re.sub('[-\s]+', '-', value)

class APISearchAdapter(SearchAdapter):
    """
    Search using the Climate Policy Radar API

    :param str api_url: The base URL of the Climate Policy Radar API
    """

    def __init__(self, api_url: str):
        self.api_url = api_url
        self.search_url = f"{api_url}/api/v1/searches"

    def search(self, parameters: SearchParameters) -> SearchResponse:
        """
        Search the Climate Policy Radar API

        :param SearchParameters parameters: a search request object
        :return SearchResponse: a list of families, with response metadata
        """
        request_payload = {}
        
        if parameters.query_string:
            request_payload["query_string"] = parameters.query_string
        if parameters.exact_match is not None:
            request_payload["exact_match"] = parameters.exact_match
        if parameters.max_hits_per_family:
            request_payload["max_passages_per_doc"] = parameters.max_hits_per_family
        if parameters.family_ids:
            request_payload["family_ids"] = parameters.family_ids
        if parameters.document_ids:
            request_payload["document_ids"] = parameters.document_ids
        if parameters.year_range:
            request_payload["year_range"] = parameters.year_range
        if parameters.sort_by:
            request_payload["sort_field"] = parameters.sort_by
        if parameters.sort_order:
            request_payload["sort_order"] = parameters.sort_order
        if parameters.continuation_tokens:
            request_payload["continuation_tokens"] = parameters.continuation_tokens
        if parameters.limit:
            request_payload["limit"] = parameters.limit
        
        keyword_filters = {}
        if parameters.filters:
            if parameters.filters.family_source:
                keyword_filters["sources"] = parameters.filters.family_source
            if parameters.filters.family_geography:
                keyword_filters["countries"] = [slugify(c) for c in parameters.filters.family_geography]
            if parameters.filters.family_category:
                keyword_filters["categories"] = parameters.filters.family_category
            if parameters.filters.document_languages:
                keyword_filters["languages"] = parameters.filters.document_languages
        
        if keyword_filters:
            request_payload["keyword_filters"] = keyword_filters

        try:
            response = requests.post(self.search_url, json=request_payload)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise QueryError(f"Error querying API: {str(e)}") from e

        response_data = response.json()
        return SearchResponse(
            total_hits=response_data["hits"],
            total_family_hits=response_data["total_family_hits"],
            query_time_ms=response_data["query_time_ms"],
            total_time_ms=response_data["total_time_ms"],
            families=[self._parse_family(family_data) for family_data in response_data["families"]],
            continuation_token=response_data["continuation_token"],
            this_continuation_token=response_data["this_continuation_token"],
            prev_continuation_token=response_data["prev_continuation_token"],
        )

    def get_by_id(self, document_id: str) -> Hit:
        """
        Get a single document by its id

        NOTE: The API spec does not include an endpoint for fetching a single document.
        This method is not implemented.

        :param str document_id: document id 
        :raises NotImplementedError: Method not supported by API
        """
        raise NotImplementedError("get_by_id is not supported by the Climate Policy Radar API")

    @staticmethod
    def _parse_family(family_data: dict) -> Family:
        return Family(
            id=family_data["family_slug"],
            hits=flatten_list([
                APISearchAdapter._parse_hit(doc_data, family_data) 
                for doc_data in family_data["family_documents"]
            ]),
            total_passage_hits=family_data["total_passage_hits"],
            continuation_token=family_data["continuation_token"],
            prev_continuation_token=family_data["prev_continuation_token"],
        )

    @staticmethod
    def _parse_hit(hit_data: dict, family_data: dict) -> Hit:
        if hit_data.get("document_passage_matches") is not None and len(hit_data.get("document_passage_matches")) > 0:
            # Passage hits
            passages = []
            for passage_data in hit_data.get("document_passage_matches"):
                passages.append(Passage(
                    family_name=family_data.get("family_name"),
                    family_description=family_data.get("family_description"),
                    family_source=family_data.get("family_source"),
                    family_import_id=family_data.get("family_import_id"),
                    family_slug=family_data.get("family_slug"),
                    family_category=family_data.get("family_category"),
                    family_publication_ts=family_data.get("family_publication_ts"),
                    family_geography=family_data.get("family_geography"),
                    document_import_id=hit_data.get("document_import_id"),
                    document_slug=hit_data.get("document_slug"),
                    document_languages=hit_data.get("document_languages"),
                    document_content_type=hit_data.get("document_content_type"),
                    document_cdn_object=hit_data.get("document_cdn_object"),
                    document_source_url=hit_data.get("document_source_url"),
                    text_block=passage_data["text"],
                    text_block_id=passage_data["text_block_id"],
                    text_block_type="text", # Not supported via API
                    text_block_page=passage_data["text_block_page"],
                    text_block_coords=passage_data["text_block_coords"]
                ))
            return passages
        else:
            # Document hit
            return Document(
                family_name=family_data.get("family_name"),
                family_description=family_data.get("family_description"),
                family_source=family_data.get("family_source"),
                family_import_id=family_data.get("family_import_id"),
                family_slug=family_data.get("family_slug"),
                family_category=family_data.get("family_category"),
                family_publication_ts=family_data.get("family_publication_ts"),
                family_geography=family_data.get("family_geography"),
                document_import_id=hit_data.get("document_import_id"),
                document_slug=hit_data.get("document_slug"),
                document_languages=hit_data.get("document_languages"),
                document_content_type=hit_data.get("document_content_type"),
                document_cdn_object=hit_data.get("document_cdn_object"),
                document_source_url=hit_data.get("document_source_url"),
            )

def get_cpr_url(slug: str) -> str:
    """Generates a URL for accessing a document on the CPR webapp given a document slug
    
    :param str slug: The slug from the search results"""
    return f"https://app.climatepolicyradar.org/document/{slug}"

def search_response_to_markdown(search_response: SearchResponse) -> str:
    """
    Generate a markdown table from a SearchResponse object.

    :param SearchResponse search_response: The search response to format
    :return str: A markdown-formatted table string
    """
    rows = []
    
    # Table header
    rows.append("| Family Title | Geography | PDF URL | Matched Passage |")
    rows.append("| --- | --- | --- | --- |")

    for family in search_response.families:
        for hit in family.hits:
            family_name = hit.family_name or ""
            family_geography = hit.family_geography or ""
            url = get_cpr_url(hit.family_slug)
            
            text_block = ""
            if isinstance(hit, Passage):
                text_block = hit.text_block

            rows.append(f"| {family_name} | {family_geography} | {url} | {text_block} |")
            

    return "\n".join(rows)
