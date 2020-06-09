@{
import html
import time
}@
<html>
  <head>
    <title>@(interface_name) Documentation</title>
    <link type="text/css" rel="stylesheet" href="../../msg-styles.css" />
  </head>
  <body>
  <div id="container">
    <h1 class="msg-title"><a href="../index-msg.html">@(interface_package)</a>/@(interface_name) @(type)</h1>
    <div class="msg">
      <h2>File: <span class="filename">@(interface_package)/@(interface_name).@(ext)</filename></h2>
      <h2>Raw Message Definition</h2>
      <div class="raw-msg">
        @(html.unescape(raw_text))
      </div>
      <h2>Compact Message Definition</h2>
      <div class="compact_definition-msg">
        @[for constant_type, constant_name in zip(constant_names, constant_types)]@
          @(constant_name)=@(constant_type) </br>
        @[end for]@
        @[for link, interface_type, interface_name in zip(links, field_types, field_names)]@
        @[if link != '']
        <a href="../../@(link)"> @(interface_type)</a> @(interface_name)</br>
        @[else]
        @(interface_type)</a> @(interface_name)</br>
        @[end if]@
        @[end for]@
      </div>
    </div>
    <p class="footer"><small><em>autogenerated on @(time.strftime("%b %d %Y %H:%M:%S", timestamp))</em></small></p>
    </div>
  </body>
</html>
