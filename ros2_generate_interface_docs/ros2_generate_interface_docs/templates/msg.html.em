@{
import html
import time
}@
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
    <title>@(interface_name) Documentation</title>
    <link type="text/css" rel="stylesheet" href="../../msg-styles.css" />
  </head>
  <body>
  <div id="container">
    <h1 class="msg-title"><a href="../index-msg.html">@(interface_package)</a>/@(interface_name) @(type)</h1>
    <div class="msg">
      <h2>File: <span class="filename">@(interface_package)/@(interface_name).@(ext)</span></h2>
      <h2>Raw Message Definition</h2>
      <div class="raw-msg">
      @[for line in raw_text.splitlines()]@
        @{text = line.strip('#')}@
        @[if '#' in line]
          <a style="color:blue">#@(html.escape(text))</a><br>
        @[else]
          @(html.escape(text))<br>
        @[end if]@
      @[end for]@
      </div>
      <h2>Compact Message Definition</h2>
      <div class="compact_definition-msg">
        @[for constant_name, constant_type in zip(constant_names, constant_types)]@
          @(constant_type) @(constant_name)<br>
        @[end for]@
        @[for relative_path, interface_type, interface_name, default_value in zip(relative_paths, field_types, field_names, field_default_values)]@
        @[if relative_path != '']
        <a href="../../@(relative_path)"> @(interface_type)</a> @(interface_name)@(default_value)<br>
        @[else]
        @(interface_type) @(interface_name)@(default_value)<br>
        @[end if]@
        @[end for]@
      </div>
    </div>
    <p class="footer"><small><em>autogenerated on @(time.strftime("%b %d %Y %H:%M:%S", timestamp))</em></small></p>
    </div>
  </body>
</html>
