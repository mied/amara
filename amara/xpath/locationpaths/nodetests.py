########################################################################
# amara/xpath/locationpaths/nodetests.py
"""
A parsed token that represents a node test.
"""

from xml.dom import Node

from amara.xpath import XPathError
from amara.xpath.locationpaths import _nodetests

__all__ = ('node_test', 'name_test')

class node_test(object):

    priority = -0.5
    node_type = None

    def getQuickKey(self, namespaces):
        """
        Returns a tuple that indicates the expected node type and, if
        applicable, the expected name.
        """
        return (self.nodeType, None)

    def pprint(self, indent='', stream=None):
        print >> stream, indent + repr(self)

    def __repr__(self):
        ptr = id(self)
        if ptr < 0: ptr += 0x100000000L
        return '<%s at 0x%x: %s>' % (self.__class__.__name__, ptr, self)

# -- NodeType classes -------------------------------------------------

class node_type(node_test):

    _classmap = {}

    class __metaclass__(type):
        def __init__(cls, name, bases, namespace):
            if 'name' in namespace:
                cls._classmap[cls.name] = cls

    def __new__(cls, name, *args):
        return object.__new__(cls._classmap[name])

    def match(self, context, node, principalType=Node.ELEMENT_NODE):
        """
        The principalType is discussed in section [2.3 Node Tests]
        of the XPath 1.0 spec.  Only attribute and namespace axes
        differ from the default of elements.
        """
        return node.nodeType == self.node_type

    def __str__(self):
        return self.name + '()'


class any_node_test(node_type):
    name = 'node'
    
    def get_filter(self, compiler, principal_type):
        return None


class comment_test(node_type):
    name = 'comment'
    node_type = Node.COMMENT_NODE

    def get_filter(self, compiler, principal_type):
        return _nodetests.type_filter(Node.COMMENT_NODE)


class text_test(node_type):
    name = 'text'
    node_type = Node.TEXT_NODE

    def get_filter(self, compiler, principal_type):
        return _nodetests.type_filter(Node.TEXT_NODE)


class processing_instruction_test(node_type):
    name = 'processing-instruction'
    node_type = Node.PROCESSING_INSTRUCTION_NODE

    def __init__(self, name, target=None):
        if target:
            self.priority = 0
            if target[:1] not in ('"', "'"):
                raise SyntaxError("Invalid literal: %r" % target)
            self._target = target[1:-1]
        else:
            self.priority = -0.5
            self._target = None

    def get_filter(self, compiler, principal_type):
        if self._target:
            return _nodetests.name_filter(Node.PROCESSING_INSTRUCTION_NODE,
                                          None, self._target)
        return _nodetests.type_filter(Node.PROCESSING_INSTRUCTION_NODE)

    def match(self, context, node, principalType=Node.ELEMENT_NODE):
        if node.nodeType != self.node_type:
            return 0
        if self._target:
            return node.target == self._target
        return 1

    def __str__(self):
        if self._target:
            target = self._target.encode('unicode_escape')
            return '%s("%s")' % (self.name, target.replace('"', '\\"'))
        return node_type.__str__(self)

# -- NameTest classes -------------------------------------------------

class name_test(node_test):
    def __new__(cls, name):
        if name[-1:] == '*':
            if ':' in name:
                cls = namespace_test
            else:
                cls = principal_type_test
        elif ':' in name:
            cls = qualified_name_test
        else:
            cls = local_name_test
        return object.__new__(cls)


class principal_type_test(name_test):

    def getQuickKey(self, namespaces):
        return (Node.ELEMENT_NODE, None)

    def get_filter(self, compiler, principal_type):
        return _nodetests.type_filter(principal_type)

    def match(self, context, node, principalType=Node.ELEMENT_NODE):
        return node.nodeType == principalType

    def __str__(self):
        return '*'


class local_name_test(name_test):

    priority = 0

    def __init__(self, name):
        self._name = name

    def getQuickKey(self, namespaces):
        return (Node.ELEMENT_NODE, (None, self._name))

    def get_filter(self, compiler, principal_type):
        return _nodetests.name_filter(principal_type, None, self._name)

    def match(self, context, node, principalType=Node.ELEMENT_NODE):
        # NameTests do not use the default namespace, just as attributes
        if node.nodeType == principalType and not node.namespaceURI:
            return node.localName == self._name
        return 0

    def __str__(self):
        return self._name


class namespace_test(name_test):

    priority = -0.25

    def __init__(self, name):
        self._prefix = name[:name.index(':')]

    def getQuickKey(self, namespaces):
        # By specifing a name of None, this test will fall into the 'general'
        # category for the principal type
        return (Node.ELEMENT_NODE, None)

    def get_filter(self, compiler, principal_type):
        try:
            namespace = compiler.namespaces[self._prefix]
        except KeyError:
            raise XPathError(XPathError.UNDEFINED_PREFIX, prefix=self._prefix)
        return _nodetests.name_filter(principal_type, namespace, None)

    def match(self, context, node, principalType=Node.ELEMENT_NODE):
        if node.nodeType != principalType:
            return 0
        try:
            return node.namespaceURI == context.processorNss[self._prefix]
        except KeyError:
            raise RuntimeException(RuntimeException.UNDEFINED_PREFIX,
                                   prefix=self._prefix)

    def __str__(self):
        return self._prefix + ':*'


class qualified_name_test(name_test):

    priority = 0

    def __init__(self, name):
        self._prefix, self._local_name = name.split(':', 1)

    def getQuickKey(self, namespaces):
        try:
            namespace = namespaces[self._prefix]
        except KeyError:
            raise XPathError(XPathError.UNDEFINED_PREFIX, prefix=self._prefix)
        return (Node.ELEMENT_NODE, (namespace, self._local_name))

    def get_filter(self, compiler, principal_type):
        try:
            namespace = compiler.namespaces[self._prefix]
        except KeyError:
            raise XPathError(XPathError.UNDEFINED_PREFIX, prefix=self._prefix)
        return _nodetests.name_filter(principal_type, namespace, self._local_name)

    def match(self, context, node, principalType=Node.ELEMENT_NODE):
        if node.nodeType == principalType:
            if node.localName == self._local_name:
                try:
                    return node.namespaceURI == context.processorNss[self._prefix]
                except KeyError:
                    raise RuntimeException(RuntimeException.UNDEFINED_PREFIX,
                                           prefix=self._prefix)
        return 0

    def __str__(self):
        return self._prefix + ':' + self._local_name
