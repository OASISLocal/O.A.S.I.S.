<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:atom="http://www.w3.org/2005/Atom">
<xsl:output method="html" encoding="UTF-8" indent="yes"/>
<xsl:template match="/atom:feed">
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title><xsl:value-of select="atom:title"/> — preview</title>
<style>
body{margin:0;background:#111;color:#c9c9c9;font-family:Inter,-apple-system,sans-serif;line-height:1.7;-webkit-font-smoothing:antialiased}
.wrap{max-width:720px;margin:0 auto;padding:56px 24px 80px}
.badge{display:inline-block;font-family:ui-monospace,monospace;font-size:10px;letter-spacing:.12em;text-transform:uppercase;color:#fff;border:1px solid #fff;padding:5px 10px;margin-bottom:14px}
h1{font-family:'Space Grotesk',Inter,sans-serif;color:#fff;letter-spacing:-.03em;font-size:34px;margin:0 0 8px}
.sub{color:#8f8f8f;font-size:15px;margin-bottom:8px}
.note{border:1px solid rgba(255,255,255,.16);border-left:2px solid #fff;padding:10px 14px;font-size:13.5px;color:#8f8f8f;margin:22px 0 30px}
.note code{font-family:ui-monospace,monospace;font-size:.85em;border:1px solid rgba(255,255,255,.16);padding:1px 6px}
ol{list-style:none;margin:0;padding:26px 0 0;border-top:2px solid #fff}
li{padding:20px 0;border-bottom:1px solid rgba(255,255,255,.16)}
li a.t{color:#fff;font-weight:700;font-size:18px;text-decoration:none}
li a.t:hover{text-decoration:underline}
li .d{font-family:ui-monospace,monospace;font-size:11px;color:#8f8f8f;text-transform:uppercase;letter-spacing:.06em;display:block;margin-bottom:6px}
footer{margin-top:30px;font-family:ui-monospace,monospace;font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:#8f8f8f}
footer a{color:#c9c9c9}
</style>
</head>
<body>
<div class="wrap">
<span class="badge">Atom feed · preview</span>
<h1><xsl:value-of select="atom:title"/></h1>
<p class="sub"><xsl:value-of select="atom:subtitle"/></p>
<p class="note">You are looking at a styled preview. To follow new posts, copy this page's address into any feed reader, or open <code><xsl:value-of select="atom:link[@rel='self']/@href"/></code> in yours.</p>
<ol>
<xsl:for-each select="atom:entry">
<li>
<span class="d"><xsl:value-of select="substring(atom:updated,1,10)"/></span>
<a class="t" href="{atom:link/@href}"><xsl:value-of select="atom:title"/></a>
</li>
</xsl:for-each>
</ol>
<footer><a href="../">← Back to OASIS</a></footer>
</div>
</body>
</html>
</xsl:template>
</xsl:stylesheet>
