import pyvisa

def find_resources():
    """Find all connected resources using PyVISA."""
    rm = pyvisa.ResourceManager()
    resources = rm.list_resources()
    
    if not resources:
        print("No resources found.")
    else:
        print("Connected resources:")
        for resource in resources:
            print(resource)
    
    return resources

def resource_info(resource):
    """
    Get detailed information about a specific resource. By printing their response to de *IDN? Visa command.
    Args:
        resource: ID of the resource.
    """
    rm = pyvisa.ResourceManager()
    try:
        inst = rm.open_resource(resource)
        info = inst.query("*IDN?")
        print(f"Resource: {resource}, Info: {info}")
    except Exception as e:
        print(f"Error accessing resource {resource}: {e}")

def list_resources():
    """
    Prints the resources and their information
    """
    res = find_resources()
    for r in res:
       resource_info(r)

if __name__ == "__main__":
   list_resources()
    