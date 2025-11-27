# Copyright (c) 2025 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from django import template

register = template.Library()


@register.filter
def host_interface(facts, interface):
    """
    Get interface data from Ansible facts.
    Ansible stores detailed interface information under keys like:
    - ansible_<interface_name> (e.g., ansible_eth0, ansible_enp0s3)

    Args:
        facts: The host.facts dictionary
        interface: The interface name (e.g., 'eth0', 'enp0s3')

    Returns:
        Dictionary with interface data or None if not found
    """
    if not facts or not interface:
        return None

    # Try to get the interface data with ansible_ prefix
    interface_key = f"ansible_{interface}"
    interface_data = facts.get(interface_key)

    return interface_data if interface_data else None
