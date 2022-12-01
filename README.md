# pp_cmd_fit_apply
Postprocessing commands "fit" and "apply"

Usage example:  
```
... | fit lr "col" from "col1, col2, col3" into <model_name>
```  
```
... | apply <model_name>
```  
```
... | get_coef <model_name>
```
```
... | prophet value, future=101, period='D', modelType=additive
```
Saving into private storage:  
```
... | fit lr "col" from "col1, col2, col3" into <model_name>, private=True
```  
Load from private storage:
```
... |  apply <model_name>, private=True
```  
Model name may include relative path 
```
... | fit lr "col" from "col1, col2, col3" into "<dir_name1/dir_name2/model_name>"
```  
## Getting started
1. Make develop python virtual environment
    ```bash
    make dev
    ```
2. Configure `otl_v1` command
    ```bash
    vi venv/lib/python3.9/site-packages/postprocessing_sdk/pp_cmd/otl_v1/config.ini
    ```
3. Activate virtual environment
   ```bash
   source ./venv/bin/activate
   ```
4. Launch post-processing interpreter
   ```bash
   pp
   ```
5. Make sure that `otl_v1 ` works
  | otl_v1 <# makeresults count=3 #>
