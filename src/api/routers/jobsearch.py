from fastapi import APIRouter, Query
from typing import List, Optional
from pydantic import BaseModel
import urllib.parse

router = APIRouter()

class JobPortalResult(BaseModel):
    portal: str
    icon: str
    color: str
    title: str
    url: str

class JobSearchResponse(BaseModel):
    status: str
    data: List[JobPortalResult]

JOB_PORTALS = [
    {
        "name": "LinkedIn",
        "icon": "fab fa-linkedin",
        "color": "#0A66C2",
        "base_url": "https://www.linkedin.com/jobs/search/?keywords={keyword}&location={location}"
    },
    {
        "name": "Naukri",
        "icon": "fas fa-building",
        "color": "#FF7555",
        "base_url": "https://www.naukri.com/{keyword}-jobs-in-{location}"
    },
    {
        "name": "Indeed",
        "icon": "fas fa-search-dollar",
        "color": "#003A9B",
        "base_url": "https://in.indeed.com/jobs?q={keyword}&l={location}"
    },
    {
        "name": "Foundit",
        "icon": "fas fa-globe",
        "color": "#5D3FD3",
        "base_url": "https://www.foundit.in/srp/results?query={keyword}&locations={location}"
    }
]

def format_url_param(param: str, portal_name: str) -> str:
    """Format query parameters strictly based on target portal standard."""
    if not param:
        return ""
    
    clean_param = param.lower().strip()
    if portal_name in ["LinkedIn", "Indeed"]:
        return urllib.parse.quote(clean_param)
    return clean_param.replace(" ", "-")

@router.get("/search", response_model=JobSearchResponse)
async def search_jobs(
    keyword: str = Query(..., min_length=2, description="Job title or skills"),
    location: Optional[str] = Query("Remote", description="Target working location")
):
    results = []
    
    for portal in JOB_PORTALS:
        formatted_keyword = format_url_param(keyword, portal["name"])
        formatted_location = format_url_param(location, portal["name"])
        
        final_url = portal["base_url"].format(
            keyword=formatted_keyword, 
            location=formatted_location
        )
        
        results.append(JobPortalResult(
            portal=portal["name"],
            icon=portal["icon"],
            color=portal["color"],
            title=f"Find {keyword} jobs in {location} on {portal['name']}",
            url=final_url
        ))
        
    return JobSearchResponse(status="success", data=results)