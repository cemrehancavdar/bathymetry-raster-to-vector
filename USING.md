# Install Prerequisites

## Install Pixi
```sh
curl -fsSL https://pixi.sh/install.sh | bash
```

## Download pg_tileserv
Download the latest version of pg_tileserv for your OS:
```sh
https://postgisftw.s3.amazonaws.com/pg_tileserv_latest_{OS_VERSION}.zip
```
Unzip the file to `/source/pg_tileserv`.

## Install Pixi Environment
```sh
cd source
pixi install
```

# Run Processing Commands

In the current working directory `/source`, run the following commands:
first export 
```sh
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/postgres
pixi run generate
pixi run simplify
pixi run smooth
pixi run upload
pixi run serve
pixi run map
```