# Netbox Ninja Plugin Examples

This document provides practical examples of using the Netbox Ninja Plugin.

## Basic Example: Region and Sites Visualization

Assume we have the following sites in region `Region1` in Netbox:

![Sites](images/sites.png)

### Step 1: Create a Draw.io Diagram

Let's draw a simple picture with [draw.io](https://www.drawio.com):

![Draw.io](images/draw-io.png)

### Step 2: Add Dynamic Content

After saving the drawing, we'll get a draw.io format XML file. We can make the drawing dynamic by adding Netbox data to it. Here's how to add Jinja tags for regions and sites:

```xml
<mxfile host="Electron" agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) draw.io/26.2.2 Chrome/134.0.6998.178 Electron/35.1.2 Safari/537.36" version="26.2.2">
  <diagram name="Page-1" id="nSQkXgtPt4yLN-CesYIH">
    <mxGraphModel dx="803" dy="932" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="850" pageHeight="1100" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <mxCell id="IldwPKkJlOeXaoglpFC2-4" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=0.5;exitY=1;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;" edge="1" parent="1" source="IldwPKkJlOeXaoglpFC2-1" target="IldwPKkJlOeXaoglpFC2-2">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="IldwPKkJlOeXaoglpFC2-5" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=0.5;exitY=1;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;" edge="1" parent="1" source="IldwPKkJlOeXaoglpFC2-1" target="IldwPKkJlOeXaoglpFC2-3">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="IldwPKkJlOeXaoglpFC2-1" value="{{ regions.get(slug='region1') }}" style="rounded=0;whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="360" y="160" width="120" height="60" as="geometry" />
        </mxCell>
        <mxCell id="IldwPKkJlOeXaoglpFC2-2" value="{{ sites.get(slug='site1') }}" style="rounded=0;whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="270" y="280" width="120" height="60" as="geometry" />
        </mxCell>
        <mxCell id="IldwPKkJlOeXaoglpFC2-3" value="{{ sites.get(slug='site2') }}" style="rounded=0;whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="450" y="280" width="120" height="60" as="geometry" />
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

### Step 3: Create a Ninja Template

Navigate to NetBox's Ninja Templates section and create a new template:

![Ninja Templates](images/ninja-templates.png)

The template creation form includes the following fields:

* **Name**: Name for this Ninja template
* **Output type**: Either render the template to text output or Draw.io format picture
* **Object types**: Assign this template to zero or more Netbox objects. Selected object views will get a new "Ninja" tab where the output is rendered
* **Tags**: Add normal Netbox tags to this template
* **Code**: Add your template code here

![Add a new Ninja Template](images/add-a-new-ninja-template.png)


### Step 4: View the Results

After creating the template, you'll see the rendered diagram:

![Regions and Sites](images/regions-and-sites.png)

### Step 5: Object-Specific Templates

You can make the template object-specific by adding `DCIM > Region` to `Object types` and using the `{{ target_object.name }}` tag. When viewing a specific region in Netbox, you'll see a new tab:

![Region1](images/region1.png)
