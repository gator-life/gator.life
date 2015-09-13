# -wget http://storage.googleapis.com/gcd/tools/gcd-v1beta2-rev1-3.0.0.zip  -nv
# - unzip -q gcd-v1beta2-rev1-3.0.0.zip -d lib
lib/gcd-v1beta2-rev1-2.1.1/gcd.sh create --dataset_id=gator-01 temp/test_dataset
lib/gcd-v1beta2-rev1-2.1.1/gcd.sh start --port=33001 temp/test_dataset &
./lib/google_appengine/dev_appserver.py ./src/server/server/ --skip_sdk_update_check &