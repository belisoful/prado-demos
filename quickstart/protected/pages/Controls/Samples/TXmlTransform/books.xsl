<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
	<xsl:output method="html" encoding="UTF-8" omit-xml-declaration="yes" indent="no"/>
	<xsl:param name="heading">Books</xsl:param>

	<xsl:template match="/books">
		<h3><xsl:value-of select="$heading"/></h3>
		<table class="sampletable">
			<tr><th>Title</th><th>Author</th><th>Year</th></tr>
			<xsl:for-each select="book">
				<tr>
					<td><xsl:value-of select="title"/></td>
					<td><xsl:value-of select="author"/></td>
					<td><xsl:value-of select="@year"/></td>
				</tr>
			</xsl:for-each>
		</table>
	</xsl:template>
</xsl:stylesheet>
