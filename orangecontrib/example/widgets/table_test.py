from Orange.data import ContinuousVariable,Domain
import numpy
import Orange

domain = in_data.domain

new_table = in_data.copy()
attrList=list(domain.attributes)

newValues=[]
i=0

for row in new_table:
    sum=0
    max=0
    min=1e10
    stddev=0
    abs=0
    normValues=[]
    n=0
    for attr in row.domain.attributes:
        if (isinstance(attr,ContinuousVariable) and (attr.name.startswith('F'))):                        
            if(i==0):
                newAttr=ContinuousVariable('norm'+attr.name)                
                attrList.append(newAttr)
            val=row[attr]
            sum+=val
            
            if(val>max): max=val
            if(val<min): min=val
            
            normValues.append(row[attr])
            abs=row[attr]*row[attr]
            stddev+=(row[attr]-mean)**2
            
            n+=1
    i+=1
    mean=sum/n
    sttdev = numpy.sqrt(stddev)/(n-1)
    abs=numpy.sqrt(abs)
    addArray=list(numpy.asarray(normValues)/mean)
    addArray.extend([sum,max,min,mean,abs,sttdev])
    newValues.append(numpy.asarray(addArray))
    
attrList.extend([ContinuousVariable('Sum'), \
ContinuousVariable('Max'), \
ContinuousVariable('Min'), \
ContinuousVariable('Mean'), \
ContinuousVariable('Abs'), \
ContinuousVariable('StdDev')])

cols_to_add=numpy.asarray(newValues)
new_table=numpy.append(new_table,cols_to_add,axis=1)

new_attributes=tuple(attrList)
new_domain=Domain(attributes=new_attributes, \
metas=domain.metas, \
class_vars=domain.class_vars)

new_table=Orange.data.Table.from_numpy(new_domain,new_table)

out_data=new_table