# CENACS
Clean Energy kNowledge Analysis for preComputed Simulation data

To use this project, install docker, clone the repo, and `cd` to the top level.

### Architecture

Here's the current state of our project. Please note that in the future we plan to move data processing and bulk upload onto our server.

![Site architecture](https://bescienceswebsite.blob.core.windows.net/misc/website_architecture_deckgl.png)

### Development
To run the development environment, set `COSMOS_KEY=<COSMOS_KEY_HERE>` in your local environment. Do the same for `COSMOS_DB_NAME` and `COSMOS_ENDPOINT` (ask the team for the correct values). Then run:

```
docker-compose up
```

Then you should see the site at [http://localhost:3000/](http://localhost:3000/) and you can access the API at [http://localhost:8000/graphql](http://localhost:8000/graphql).

Here you should see an interactive graphql query tool. Try the following query:

```
{
	powerGeneration(
      scenarioId: 270,
  		locationRollup:INTERCONNECT,
  		timeRollup:YEAR) {
        resourceType
        generation
    }
}
```

You should see a bunch of data spit out on the right hand side of the page.

### Production
To run the production build locally, make sure you're at top level of the repo. Then run:

```
docker build -t cenacs:latest $PWD
docker run -it --rm -p 8000:8000 -e PRODUCTION_HOST=localhost -e SECRET_KEY=anyKeyWorksHere -e COSMOS_KEY=$COSMOS_KEY -e COSMOS_DB_NAME=$COSMOS_DB_NAME -e COSMOS_ENDPOINT=$COSMOS_ENDPOINT -e CRM_AUTHORITY=$CRM_AUTHORITY -e CRM_CLIENT_ID=$CRM_CLIENT_ID -e CRM_ENDPOINT=$CRM_ENDPOINT -e CRM_SCOPE=$CRM_SCOPE -e CRM_SECRET=$CRM_SECRET -e AZURE_INSTRUMENTATION_KEY=$AZURE_INSTRUMENTATION_KEY -e PORT=8000 cenacs:latest
```

For more information about the frontend, checkout the [frontend README](./frontend/README.md)

### Before creating a PR
Please follow PR guidelines here: [https://github.com/intvenlab/REISE/wiki/Pull-Request-Etiquette](https://github.com/intvenlab/REISE/wiki/Pull-Request-Etiquette)

For CENACS, we also need to:
* Run the production build to make sure it works
* Check visuals in Chrome, Firefox, Safari, and Edge
  * For most of these testing in Dev is fine
  * You will want to enable developer tools on each browser
* Run `yarn lint`
* Run `yarn test .`
  * You need to specify a directory otherwise yarn only runs tests in changed files

## Testing

We have unit tests and a few integration tests for both the backend and the frontend. The frontend tests are run with `yarn test` and selenium, while the backend tests are run with `pytest`.

Before deploying, we also recommend doing a couple of quick smoke tests. Please see [Smoke Testing and Manual Testing](https://github.com/Breakthrough-Energy/CENACS/wiki/Smoke-Testing-and-Manual-Testing).

Before testing the backend, please set `DJANGO_SETTINGS_MODULE=cenacs.settings.development` in your local environment. This lets pytest-django run tests correctly.

### Supported Browsers

Currently we support a fairly simple list of browsers:

* Chrome (latest)
* Edge (latest) -- important despite market share due to dog-fooding
* Safari (latest) -- often has some black-sheep bugs that are not present in other browsers
* Firefox (latest)
* Android Chrome (latest) -- watch for bugs when using 100vh in css
* iOS Safari (latest) -- tends to mirror bugs in desktop safari

When making major feature or style changes, please take care to test mobile browsers!
Note that we have chosen not to support Internet Explorer as Microsoft is currently phasing it out.

#### Testing Browsers on Windows
If you are on Mac or Linux, will need to download a VM
* Install virtualbox: https://www.virtualbox.org/wiki/Downloads
* Setup the official windows VM: https://developer.microsoft.com/en-us/microsoft-edge/tools/vms/
* Build and run the production docker container. For more info see above.
  * Set  `PRODUCTION_HOST=10.0.2.2`
* In the VM, access the site at `10.0.2.2:8000`. This is the bridge between the VM and your `localhost`.

### Supported Resolutions
We utilize responsive css -- breakpoints are at 900px, 1200px, and 1800px. The minimum page width we look at is 360px. Scrollytelling has major style changes at 1200px as its two columns require a wider screen. The dashboard is more flexible and switches over to a reduced featureset at 900px.

## Troubleshooting
### I'm having vague docker problems!
Try ssh-ing into your docker container.

```
docker ps
docker exec -it <your_container_name> /bin/bash
```

### Docker is taking up a ton of space on my computer!
You can prune dead containers, images, networks and volumes. It is a good idea to do this regularly.

```
docker system prune --all --volumes
```

### I tried to install a new package to the frontend and it didn't work!
Our node modules are stored in a volume `cenacs_nodemodules` managed by docker that lives outside of the container instances.
When you run `docker-compose build`, this volume is reused even when the `--no-cache` flag is set.
The reason we have this is so that we do not have to reinstall node modules every time the container is built, speeding up things considerably.

To rebuild the volume, run:

```
docker-compose down --volumes
docker-compose build --no-cache
```

As a last resort you may blow away containers, images, or volumes manually.

```bash
# Remove containers
docker rm $(docker ps -a -q)

# Remove images
docker rmi $(docker images -a -q)

# Remove volumes
docker volume rm $(docker volume ls -q)
```
