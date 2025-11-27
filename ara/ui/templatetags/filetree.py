# Copyright (c) 2025 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from django import template

register = template.Library()


def build_tree(files):
    """
    Convert a flat list of file dicts with paths into a nested tree structure.

    Args:
        files: List of file dictionaries with 'path' and 'id' keys

    Returns:
        List of tree nodes, where each node is a dict with:
        - name: str (directory or file name)
        - path: str (full path)
        - is_file: bool
        - file_id: int or None (only for files)
        - children: list of child nodes (only for directories)
    """
    root = {"children": {}}

    for file_dict in files:
        # Handle both dict access and attribute access for flexibility
        if isinstance(file_dict, dict):
            path = file_dict.get("path", "")
            file_id = file_dict.get("id")
        else:
            path = getattr(file_dict, "path", "")
            file_id = getattr(file_dict, "id", None)

        parts = [p for p in path.split("/") if p]  # Split and remove empty parts

        current = root
        current_path = ""

        for i, part in enumerate(parts):
            current_path += "/" + part
            is_last = i == len(parts) - 1

            if part not in current["children"]:
                current["children"][part] = {
                    "name": part,
                    "path": current_path,
                    "is_file": is_last,
                    "file_id": file_id if is_last else None,
                    "children": {} if not is_last else None,
                }
            elif is_last:
                # Update existing entry if this is a file
                current["children"][part]["is_file"] = True
                current["children"][part]["file_id"] = file_id

            current = current["children"][part]

    def dict_to_list(node):
        """Convert children dict to sorted list recursively"""
        if node.get("children") is None:
            return node

        children_list = []
        # Sort: directories first, then files, both alphabetically
        sorted_children = sorted(node["children"].values(), key=lambda x: (x["is_file"], x["name"].lower()))
        for child in sorted_children:
            children_list.append(dict_to_list(child))

        node["children"] = children_list
        return node

    result = dict_to_list(root)
    return result.get("children", [])


@register.filter
def as_filetree(files):
    """
    Template filter to convert serialized files queryset to tree structure.

    Usage in template:
        {% with tree=files|as_filetree %}
            {% include "partials/filetree_node.html" with nodes=tree %}
        {% endwith %}
    """
    return build_tree(files)
