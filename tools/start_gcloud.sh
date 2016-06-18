# kill previous instance of gcloud and free port if needed
pkill gcloud
fuser -k 33001/tcp
gcloud --quiet beta emulators datastore start --project gator-01 --no-store-on-disk --host-port localhost:33001 --consistency=1.0