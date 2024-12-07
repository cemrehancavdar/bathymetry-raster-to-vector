# Bathymetry Task

![overview](screenshots/overview.png)
#### Overview

This project demonstrates the process of acquiring Digital Elevation Model (DEM) raster data, processing it with `GDAL` to create vector contour polygons, filtering and smoothing the data in `QGIS`, and exporting it to a `PostgreSQL` database with `PostGIS`. The contours are then served as `Mapbox Vector Tiles (MVT)` using `pg_tileserv`. Finally, the vector tiles are visualized in a web application built with `MapLibre`, showing depth with varying shades of blue.

### Workflow

#### Data Acquisition
    
The DEM data is obtained from NOAA, covering small portions of [Mobile Bay and Gulf of Mexico](https://maps.app.goo.gl/T3NSQecsMUd1XoEd7).

Tool used:
https://www.ncei.noaa.gov/maps/grid-extract/ 

#### Contour Generation

To generate vector contour polygons, I used [gdal_contour](https://gdal.org/en/latest/programs/gdal_contour.html), a CLI tool from [GDAL](https://gdal.org/en/stable/).

The code is run using pixi [^1]
```shell
pixi run gdal_contour -i 2 -p image.tiff contour.shp -amin elevation
```

###### Alternative methods
<details>

<summary>QGIS</summary>

![original image](screenshots/image.png)

The DEM Raster data can be reclassified with the <i>Reclassify By Table Tool</i>.
![reclassified image](screenshots/image-1.png)

Reclassified DEM Raster can be polygonized with <i>Polygonize (raster to vector)</i>.

![polygonized](screenshots/image-2.png)
![jagged result](screenshots/image-3.png)

This solution returns jagged results that need smoothing.

This <i><b>solution</b></i> has problems with smoothing jagged contours, which can produce small empty areas.
![smoothed-empty-areas](screenshots/image-4.png)

</details>

#### Data Processing and Filtering

The resulting vector polygons contain DEM data higher than zero. I filter and smooth the vectors using geospatial Python packages like [shapely](https://pypi.org/project/shapely/).

[shapelysmooth](https://pypi.org/project/shapelysmooth/) package used to produce smoothed contour polygons.


##### Alternative methods

<details>

<summary>QGIS</summary>

The data can be filtered with QGIS[^2] and smoothed with the <i>smooth</i> tool.


</details>

<details>

<summary>PostGIS</summary>

Data can be directly uploaded to PostgreSQL and filtered using SQL. 

PostGIS has the [ST_ChaikinSmoothing](https://postgis.net/docs/ST_ChaikinSmoothing.html) method to produce smoothed contour polygons.

</details>

#### Database Integration

I used Python's Geodataframe [to_postgis](https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.to_postgis.html) method for ease of use.

##### Alternative methods

<details>

<summary>QGIS</summary>

QGIS has an <i>Export To PostgreSQL</i> tool for ease of use.

</details>

<details>

<summary>PostGIS Tools</summary>

PostGIS has the [PostGIS Shapefile Import/Export Tool](http://www.bostongis.com/blog/index.php?/archives/186-PostGIS-2.0.0-Shapefile-GUI-Loader-and-Exporter.html) to import shapefile data with a GUI.

Another option is [shp2pgsql](https://www.bostongis.com/pgsql2shp_shp2pgsql_quickguide.bqgl) to import shapefile data via CLI.

The shp2pgsql tool might be better for automating ETL processes.

</details>

<summary>Direct SQL Calls and ORM</summary>

After processing data, it can be imported to the database programmatically using direct SQL calls or an ORM.

</details>
    

#### Tile Serving

   [pg_tileserv](https://github.com/CrunchyData/pg_tileserv) from [CrunchyData](https://www.crunchydata.com/) is ideal for serving tiles. It works by simply executing:

   ```
    export DATABASE_URL=postgresql://username:password@host/dbname
    ./pg_tileserv
   ```



##### Alternative methods

<details>

<summary>Martin</summary>

[Martin](https://github.com/maplibre/martin) is an alternative to pg_tileserv for serving vector tiles. It is a lightweight and fast vector tile server written in Rust. It can be configured to serve tiles from a PostgreSQL/PostGIS database.

To use Martin, you can run:

```
export DATABASE_URL=postgresql://username:password@host/dbname
martin serve
```

</details>

<details>

<summary>GeoServer</summary>

[GeoServer](http://geoserver.org/) is an open-source server for sharing geospatial data. It supports publishing data from various spatial data sources using open standards.

I have used GeoServer professionally to serve vector tiles and other geospatial data. It offers a robust solution for geospatial data management and visualization.

For installation, refer to the [official guide](http://geoserver.org/download/).

</details>

#### Visualization

[Maplibre](https://maplibre.org/) is used to visualize the served MVT tiles of contours. 
The map has a base layer from [OpenFreeMap](https://openfreemap.org/), which is a vector tile version of [OpenStreetMap](https://www.openstreetmap.org/).

The layer's style transitions from darker to lighter shades as elevation increases.

This is done with vanilla HTML, CSS, and JavaScript. The code is provided in the repository.

    

## Disclamer 

Initially, I tried using QGIS for the entire process, but I transitioned to Python for more automation and flexibility. I chose this approach to come up with new solutions. I've also listed alternatives methods.

I also lead the transformation of ETL processes at my company, and we use [Dagster](https://dagster.io/). IMHO, something like Dagster's [sensors](https://docs.dagster.io/concepts/partitions-schedules-sensors/sensors) feature can be used for orchestration of these kind of tasks.

## Notes

[^1]: Downloading and using GDAL can be difficult. Pixi is a new, fast, and easier tool to solve these problems. 

* https://stackoverflow.com/questions/34408699/having-trouble-installing-gdal-for-python-on-windows
* https://github.com/domlysz/BlenderGIS/wiki/How-to-install-GDAL

[^2]: The GIS world has two giants: [ESRI](https://www.esri.com)[^3] and Open Source GIS. QGIS is the heart of Open Source GIS. Even though I prefer code-based ETL, QGIS is always my first choice for <i>trying</i> new things. It also has a PyQGIS API and is extendable with the plugins.

[^3]: I worked for a year at Esri Türkiye.
