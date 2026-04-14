from .weather import get_weather
from .github import github_commit
from .execute_code import execute_code

TOOL_REGISTRY = {
    "get_weather": get_weather,
    "github_commit": github_commit,
    "execute_code": execute_code,
}
