from docutils.nodes import Element


def findall(node: Element):
    # findall replaces traverse in docutils v0.18
    # note a difference is that findall is an iterator
    return getattr(node, "findall", node.traverse)
