from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url


def print_progress(items_read):
    print("Items read: {0}".format(items_read))


def enum_items(target_list):
    items = target_list.items  # .top(1220)
    items.page_loaded += print_progress  # page load event
    ctx.load(items)
    ctx.execute_query()
    for index, item in enumerate(items):
        print("{0}: {1}".format(index, item.properties['Title']))


def get_total_count(target_list):
    """
    :type target_list: office365.sharepoint.lists.list.List
    """
    target_list.items.page_loaded += print_progress  # page load event
    result = target_list.items.get_items_count().execute_query()
    print("Total items count: {0}".format(result.value))


def get_items(target_list):
    """
    :type target_list: office365.sharepoint.lists.list.List
    """
    items = target_list.items  # .top(1220)
    items.page_loaded += print_progress  # page load event
    ctx.load(items)
    ctx.execute_query()
    print("Total items count: {0}".format(len(items)))


ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)

large_list = ctx.web.lists.get_by_title("Contacts_Large")
#get_total_count(large_list)
#get_items(large_list)
enum_items(large_list)
