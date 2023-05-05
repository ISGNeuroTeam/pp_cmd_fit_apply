# pp_cmd_fit_apply
Postprocessing commands "fit" and "apply"

Usage example:  
```
... | fit lr "col" from "col1, col2, col3" into <model_name>"
```  
```
... | apply <model_name>
```  
```
... | get_coef <model_name>
```
## prophet_fc command
```
... | prophet_fc periods=10, freq='31D', target_col='INDICATOR_VALUE', time_col='Datetime', time_epoch=yes
```
if datetime is in usual format, no parameter needed
```
... | prophet_fc periods=10, freq='12M', target_col='INDICATOR_VALUE'
```
### required parameters:
- `target_col` - to specify the name of the required data column
- `periods` - to specify amount of periods you want to get a forecast for
### optional parameters:
- `freq` - to specify the frequency of the period you want to get a  forecast for: 
for instance: `12D` - 12 days, `2M` - 2 months, `6H` - 6 hours
default is the one you have in datetime column will be specified by pandas algorithm automatically
- `time_col` - to specify the name of the datetime column. `_time` by default, if not set
- `time_epoch` - to specify if data in datetime column is in epoch format.
if datetime in epoch format then use `time_epoch` set to True: `time_epoch = True`, 
if not - set to False or do not specify at all
