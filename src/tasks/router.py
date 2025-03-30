from fastapi import APIRouter, Depends, BackgroundTasks
from .tasks import delete_old_links

router = APIRouter(prefix="/expiration_delete")

@router.get('/delete')
def delete_expired_links():
    try:
        # print(1)
        delete_old_links.apply_async()
    except Exception as e:
        return {
            'status': 503,
            'details': str(e)
        }
    return {
            'status': 200,
            'details': 'All ok'
        }