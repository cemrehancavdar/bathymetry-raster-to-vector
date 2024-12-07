import subprocess
import argparse
import fiona
from shapely.geometry import shape, mapping, MultiPolygon
from shapelysmooth import chaikin_smooth
from shapely import remove_repeated_points
import geopandas as gpd
from sqlalchemy import create_engine
import os
import webbrowser

def generate_elevation_contours(input_path, output_path):
    command = [
        "pixi",
        "run",
        "gdal_contour",
        "-i",
        "2",
        "-p",
        input_path,
        output_path,
        "-amin",
        "elevation",
    ]

    subprocess.run(command)
    print(f"Contours generated and saved to {output_path}.")


def smooth_contour_shapefile(input_path, output_path):
    with fiona.open(input_path, "r") as source:
        # Define a schema for the output shapefile
        schema = source.schema.copy()

        # Create a new shapefile to store the smoothed geometries
        with fiona.open(
            output_path,
            "w",
            driver="ESRI Shapefile",
            crs=source.crs,
            schema=schema,
        ) as sink:
            for feature in source:
                # Check if the elevation is greater than 0
                if feature["properties"].get("elevation", 0) > 0:
                    continue
                # Get the geometry of the feature
                geom = shape(feature["geometry"])

                # Smooth the geometry
                smoothed_geom = MultiPolygon(
                    [chaikin_smooth(poly) for poly in geom.geoms]
                )
                smoothed_geom = remove_repeated_points(smoothed_geom)

                # Write the smoothed geometry to the new shapefile
                sink.write(
                    {
                        "geometry": mapping(smoothed_geom),
                        "properties": feature["properties"],
                    }
                )
    print(f"Smoothed contours saved to {output_path}.")


def upload_shapefile_to_postgis(shapefile_path):
    gdf = gpd.read_file(shapefile_path)

    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise ValueError("DATABASE_URL environment variable not set")

    engine = create_engine(database_url)

    gdf.to_postgis("contour", engine, if_exists="replace")

    print(f"Data from {shapefile_path} has been uploaded to the PostgreSQL database.")


def start_pg_tileserv():
    command = ["./pg_tileserv"]
    subprocess.Popen(command, cwd="./pg_tileserv", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("pg_tileserv started in detached mode.")
    webbrowser.get("chrome").open("http://localhost:7800")


def start_http_server():
    command = ["python", "-m", "http.server", "5555"]
    subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("HTTP server started on port 5555.")
    webbrowser.get("chrome").open("http://localhost:5555/ui")

def main():
    parser = argparse.ArgumentParser(
        description="CLI tool for generating elevation contours."
    )
    parser.add_argument(
        "command",
        choices=[
            "generate_contours",
            "smooth_contours",
            "upload_to_postgis",
            "start_pg_tileserv",
            "start_http_server",
        ],
        help="Command to run",
    )

    args = parser.parse_args()

    if args.command == "generate_contours":
        generate_elevation_contours("./data/dem.tiff", "./data/contour.shp")
        return
    if args.command == "smooth_contours":
        smooth_contour_shapefile("./data/contour.shp", "./data/smoothed_contour.shp")
        return
    if args.command == "upload_to_postgis":
        upload_shapefile_to_postgis("./data/smoothed_contour.shp")
        return
    if args.command == "start_pg_tileserv":
        start_pg_tileserv()
        return
    if args.command == "start_http_server":
        start_http_server()
        return

if __name__ == "__main__":
    main()
