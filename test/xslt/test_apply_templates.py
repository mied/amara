########################################################################
# test/xslt/test_elem_attr.py
from amara.test import test_main
from amara.test.xslt import xslt_test, filesource, stringsource

class test_apply_templates_1(xslt_test):
    """`xsl:apply-templates`"""
    source = stringsource("""<?xml version="1.0"?>
<data>""" + """
 <item>b</item>
 <item in="1">a</item>
 <item>d</item>
 <item in="1">c</item>
"""*5 + """</data>""")
    transform = stringsource("""<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:template match='/'>
    <docelem>
      <xsl:apply-templates/>
    </docelem>
  </xsl:template>
  <xsl:template match='text()'/>
  <xsl:template match='item'>
    <xsl:value-of select='.'/>
  </xsl:template>
</xsl:stylesheet>
""")
    expected = """<?xml version="1.0"?>
<docelem>""" + "badc"*5 + "</docelem>"


class test_apply_templates_2(test_apply_templates_1):
    """`xsl:apply-templates` using `xsl:sort`"""
    transform = stringsource("""<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:template match='/'>
    <docelem>
      <xsl:apply-templates/>
    </docelem>
  </xsl:template>
  <xsl:template match='data'>
    <xsl:apply-templates>
      <xsl:sort/>
    </xsl:apply-templates>
  </xsl:template>
  <xsl:template match='text()'/>
  <xsl:template match='item'>
    <xsl:value-of select='.'/>
  </xsl:template>
</xsl:stylesheet>
""")
    expected = """<?xml version="1.0"?>
<docelem>""" + "a"*5 + "b"*5 + "c"*5 + "d"*5 + "</docelem>"


class test_apply_templates_3(test_apply_templates_1):
    """`xsl:apply-templates` using `xsl:with-param`"""
    transform = stringsource("""<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:template match='/'>
    <docelem>
      <xsl:apply-templates/>
    </docelem>
  </xsl:template>
  <xsl:template match='data'>
    <xsl:apply-templates>
      <xsl:with-param name='foo' select='1'/>
    </xsl:apply-templates>
  </xsl:template>
  <xsl:template match='item'>
    <xsl:param name='foo'/>
    <xsl:value-of select='concat($foo,.)'/>
  </xsl:template>
</xsl:stylesheet>
""")
    expected = """<?xml version="1.0"?>
<docelem>""" + "1b1a1d1c"*5 + "</docelem>"


class test_apply_templates_4(test_apply_templates_1):
    """`xsl:apply-templates` using `xsl:sort` and `xsl:with-param`"""
    transform = stringsource("""<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:template match='/'>
    <docelem>
      <xsl:apply-templates/>
    </docelem>
  </xsl:template>
  <xsl:template match='data'>
    <xsl:apply-templates>
      <xsl:sort/>
      <xsl:with-param name='foo' select='1'/>
    </xsl:apply-templates>
  </xsl:template>
  <xsl:template match='item'>
    <xsl:param name='foo'/>
    <xsl:value-of select='concat($foo,.)'/>
  </xsl:template>
</xsl:stylesheet>
""")
    expected = """<?xml version="1.0"?>
<docelem>""" + "1a"*5 + "1b"*5 + "1c"*5 + "1d"*5 + "</docelem>"


class test_apply_templates_5(test_apply_templates_1):
    """`xsl:apply-templates` with select"""
    transform = stringsource("""<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:template match='/'>
    <docelem>
      <xsl:apply-templates select='data/item[@in]'/>
    </docelem>
  </xsl:template>
  <xsl:template match='item'>
    <xsl:value-of select='.'/>
  </xsl:template>
</xsl:stylesheet>
""")
    expected = """<?xml version="1.0"?>
<docelem>""" + "ac"*5 + "</docelem>"


class test_apply_templates_6(test_apply_templates_1):
    """`xsl:apply-templates` with select of attributes"""
    transform = stringsource("""<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:template match='/'>
    <docelem>
      <xsl:apply-templates select='data/item/@in'/>
    </docelem>
  </xsl:template>
  <xsl:template match='@*[. = "1"]'>!</xsl:template>
</xsl:stylesheet>
""")
    expected = """<?xml version="1.0"?>
<docelem>""" + "!!"*5 + "</docelem>"


class test_apply_templates_7(test_apply_templates_1):
    """`xsl:apply-templates` with select using `xsl:sort`"""
    transform = stringsource("""<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:template match='/'>
    <docelem>
      <xsl:apply-templates/>
    </docelem>
  </xsl:template>
  <xsl:template match='data'>
    <xsl:apply-templates select='item[@in]'>
      <xsl:sort/>
    </xsl:apply-templates>
  </xsl:template>
  <xsl:template match='item'>
    <xsl:value-of select='.'/>
  </xsl:template>
</xsl:stylesheet>
""")
    expected = """<?xml version="1.0"?>
<docelem>""" + "a"*5 + "c"*5 + "</docelem>"


class test_apply_templates_8(test_apply_templates_1):
    """`xsl:apply-templates` with select using `xsl:with-param`"""
    transform = stringsource("""<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:template match='/'>
    <docelem>
      <xsl:apply-templates/>
    </docelem>
  </xsl:template>
  <xsl:template match='data'>
    <xsl:apply-templates select='item[@in]'>
      <xsl:with-param name='foo' select='1'/>
    </xsl:apply-templates>
  </xsl:template>
  <xsl:template match='item'>
    <xsl:param name='foo'/>
    <xsl:value-of select='concat($foo,.)'/>
  </xsl:template>
</xsl:stylesheet>
""")
    expected = """<?xml version="1.0"?>
<docelem>""" + "1a1c"*5 + "</docelem>"


class test_apply_templates_9(test_apply_templates_1):
    """`xsl:apply-templates` with select using `xsl:sort` and `xsl:with-param`"""
    transform = stringsource("""<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:template match='/'>
    <docelem>
      <xsl:apply-templates/>
    </docelem>
  </xsl:template>
  <xsl:template match='data'>
    <xsl:apply-templates select='item[@in]'>
      <xsl:sort/>
      <xsl:with-param name='foo' select='1'/>
    </xsl:apply-templates>
  </xsl:template>
  <xsl:template match='item'>
    <xsl:param name='foo'/>
    <xsl:value-of select='concat($foo,.)'/>
  </xsl:template>
</xsl:stylesheet>
""")
    expected = """<?xml version="1.0"?>
<docelem>""" + "1a"*5 + "1c"*5 + "</docelem>"


if __name__ == '__main__':
    test_main()