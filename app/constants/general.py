"""General Constants."""
APP_NAME = "app"
APP_ROOT_KEY = "APP_ROOT"

UTF8 = "utf8"
ASCII = "ascii"
IDNA = "idna"
SECRET_KEY = "secret_key"  # nosec
SESSION_COOKIE_NAME = "session_cookie_name"
SESSION_ID = "session_{0}"
USER = "user"
SHARED = "shared"
NAME = "name"
ACCESS_KEY = "access_key"
CONTEXT = "context"
APP_ID = "app_id"
SEC_KEY = "SEC"
HTTPS = "https://"

ALNIC = "ALNIC"
KEY_NAME = "key_name"
ELEMENT_TYPE = "element_type"
OUTER_KEY_LABEL = "outer_key_label"
KEY_NAME_TYPES = "key_name_types"
EIQ_VALUE = "eiq_value"

GLUE_COLON = ":"
GLUE_HYPHEN = "-"
EMPTY_STRING = ""
SPACE_STRING = " "
COMMA_STRING = ","
COMMA_SPACE_STRING = ", "
NEW_LINE = "\n"
WINDOWS_NEW_LINE = "\r\n"
TAB_STRING = "\t"
PIPE_STRING = "|"
CAROT_STRING = "^"
SLASH = "/"
UNDERSCORE = "_"
PLUS = "+"
GLUE_COLONS = ":::"
EQUAL_TO = "="
STR_ZERO = "0"

STATUS_CODE = "status_code"
STATUS_STRING = "status"
MESSAGE_STRING = "message"
ERROR_STRING = "error"
# Status code
STATUS_CODE_500 = 500
STATUS_CODE_400 = 400
STATUS_CODE_404 = 404
STATUS_CODE_401 = 401
STATUS_CODE_403 = 403
STATUS_CODE_200 = 200
STATUS_CODE_201 = 201
STATUS_CODE_202 = 202
STATUS_CODE_422 = 422
STATUS_CODE_409 = 409

# constants for Log levels
LOG_LEVEL_DEBUG = "debug"
LOG_LEVEL_INFO = "info"
LOG_LEVEL_WARNING = "warning"
LOG_LEVEL_CRITICAL = "critical"
LOG_LEVEL_ERROR = "error"
LOG_LEVEL_EXCEPTION = "exception"

# Auth credentials
HOST = "host"
API_KEY = "api_key"  # nosec
QRADAR_SECURITY_TOKEN = "qradar_security_token"  # nosec
VERSION = "version"  # nosec
AUTH_USER = "auth_user"  # nosec
SECURITY_TOKEN = "security_token"  # nosec
INTERVAL = "interval"

BEARER_TOKEN = "BEARER_TOKEN"  # nosec
NO_AUTH = "NO_AUTH"  # nosec

# APIs
GET = "get"
POST = "post"
DELETE = "delete"
HEADERS = "headers"
LIMIT = "limit"
OFFSET = "offset"
FILTER_LAST_UPDATED_AT = "filter[>last_updated_at]"
FILTER_OUTGOING_FEEDS = "filter[outgoing_feeds]"
SORT = "sort"

LAST_UPDATED_AT = "last_updated_at"
EIQ = "eiq"
EIQ_ = "eiq_"
VALUE = "value"
RANGE = "RANGE"
ITEMS = "items=0-2"

NAME = "name"
DATA = "data"
COUNT = "count"
OBSERVABLES = "observables"
OBSERVABLE_TYPES = "observable_types"
OUTGOING_FEEDS = "outgoing_feeds"
BACKFILL_TIME = "backfill_time"
OBSERVABLE_TIME_TO_LIVE = "observable_time_to_live"
SELF = "self"
PERMISSIONS = "permissions"
META = "meta"

# OBSERVABLE TYPES
TYPE = "type"

CVE = "cve"
IP = "ip"
FILEHASH = "file_hash"
EMAIL = "email"
DOMAIN = "domain"
HASH = "hash"

# Observable data keys
CREATED_AT = "created_at"
ID = "id"
DESC_BY_LAST_UPDATED_AT = "-last_updated_at"
MALICIOUSNESS = "maliciousness"
VALUE = "value"
META = "meta"
VERSION_1 = "v1"
RANGE = "RANGE"
# Templates
HELLO_TEMPLATE = "hello.html"
SETUP_TEMPLATE = "setup.html"

# Configs
TIMEOUT = "timeout"
MAX_RETRY = "max_retry"
RETRY_INTERVAL = "retry_interval"
VERIFY_SSL = "VERIFY_SSL"
PAGE_SIZE = "PAGE_SIZE"

# Permissions for EIQ platform
READ_ENTITIES = "read entities"
MODIFY_EXTRACTS = "modify entities"
READ_EXTRACTS = "read extracts"
READ_OUTGOING_FEEDS = "read outgoing-feeds"
READ_PERMSSIONS = "read permissions"
TIME_MILLISECOND = 1000

# Return
MULTI_RESULTS = "Multi results"

DESC_KEY = "description"
VALUE_KEY = "value"
SCRIPT_KEY = "script"

# Sighting fields
TITLE = "title"
TIME_STAMP = "timestamp"
TIME_KEY = "time"
META_KEY = "meta"
SECURITY_CONTROL = "security_control"
START_TIME = "start_time"
TAGS_KEY = "tags"
INGEST_TIME_KEY = "ingest_time"
CONFIDENCE_KEY = "confidence"
MEDIUM = "Medium"
STR_TWO = "2"
EIQ_SIGHTING = "eiq_sighting"
IPV4 = "ipv4"
DOMAIN = "domain"
EMAIL = "email"
URL = "url"
URI = "uri"
MD5_HASH = "hash-md5"
SIGHTING_VALUE = "sighting_value"
SIGHTING_DESC = "sighting_description"
SIGHTING_TITLE = "sighting_title"
SIGHTING_TAGS = "sighting_tags"
SIGHTING_TYPE = "sighting_type"

LABELS = "labels"
LABEL_DATA = "label_data"
SORTED_TIME = "sorted_time"

PIE_CHART_MAX_LABELS = 7
PIE_CHARTS_OTHERS = "Others"

INDICATOR_TYPE = "indicator_type"
CONFIDENCE_LEVEL = "confidence_Level"
SEARCH_SIGHTING_COUNT_BY_CONFIDENCE = "SEARCH_SIGHTING_COUNT_BY_CONFIDENCE"
SEARCH_SIGHTING_COUNT_BY_TIME = "SEARCH_SIGHTING_COUNT_BY_TIME"
SEARCH_SIGHTING_COUNT_BY_OBSERVABLE_TYPE = "SEARCH_SIGHTING_COUNT_BY_OBSERVABLE_TYPE"

# FILTERS
SELECT_LEVEL = "select_level"
SELECT_TYPE = "select_type"
START_TIME = "start_time"
END_TIME = "end_time"

# types of chart
PIE_DATA = "pie_data"
BAR_CHART1 = "bar_chart1"
BAR_CHART2 = "bar_chart2"

I_TYPE_ALL = "all"
C_LEVEL_UNKNOWN = "unknown"
LOW = "low"
MEDIUM = "medium"
HIGH = "high"

# Certificates
IS_SELF_SIGNED_CERT = "is_self_signed_cert"
STORE = "store"
CERTS = "certs"
CERT_FILE = "certfile.pem"

VERIFY_SSL = "verify_ssl"

CERTIFICATE_FILE = 'certificate_file'

