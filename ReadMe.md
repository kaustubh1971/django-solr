## Installing required packages

Ensure that the virtualenv is active and run the following from the
repository root.

```
pip install -r requirements.txt
```

## Install Apache Solr
1. Check Whether java is installed or not ? if not then install it first
```bash
java --version
```

2. Install solr

```bash
sudo wget https://archive.apache.org/dist/lucene/solr/8.9.0/solr-8.9.0.tgz
sudo tar xzf solr-8.9.0.tgz
sudo bash solr-8.9.0/bin/install_solr_service.sh solr-8.9.0.tgz
sudo systemctl status solr
```

3. Now visit your browser

- localhost:8983
- You will get solr running locally

### Build and install the solr schema


4. Crate Core locally
- Address could be differen according to your own system where you have stored solr at ith core name **new_solr_test**
```
sudo su - solr -c "/home/auergine/test/solr-8.9.0/bin/solr create -c job_application -n data_driven_schema_configs"
```

5. Now migrate those changes

```bash
python manage.py makemigrations
python manage.py migrate
```

6. Generate your schema on Solr by visiting localhost:8983 location for a specific core
   - This is a very important point if you dont do that them your datatype wont be proper since we describe the datatypes in django(python) which are not supported by Java. 

| fields                  | types  |
|-------------------------|--------|
| name                    | string |
| email | string |                   
| why_us | string |                  
| why_you | string |                 
| social_profile_link | string |     
| resume_link | string |             
| mobile_number | string |           
| role | string |                    
| other_role | string |              
| experience | string |              
| preferred_location | string |      
| preferred_time_for_call | string | 
| current_ctc | pint   |             
| notice_period | pint   |           
| timestamp| pdate  |



7. Install solr schema  
```
python manage.py build_solr_schema > schema.xml
```

8. Restart your locally installed solr
```
sudo systemctl restart solr
```

9. Skip this if you already have credentials.json 
- Create Your Google project to access the google sheet [Video link](https://www.youtube.com/watch?v=3wC-SCdJK2c)
- After downloading the credentials store it in solr_app with name credentials.json for further processing

### Load data in your index

10. Run below command which will generate the data in Solr
```
python solr_app/load.py
```

   - Might take some time to load the data you can refresh your solr UI page to get how much data is Generated


### Update Solr Index

**Changes to the Database Aren't Reflected in Search Results**

```lang=sh
python manage.py update_index
```

This command updates the Solr index with any changes which are not currently
reflected. 