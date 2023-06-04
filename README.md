**DataExplore** is simple tool we can utilise to natural language to communicate with data and create insights out of it. This works with any rdbms database. 
This framework utilizes 2 major components. One is LangChain and the second is visualization tools. you can see the code in my GitHub along with a demo video.

**LangChain**: I have used _**SQLDatabaseChain**_. I have overridden the default prompt template to receive the naturally speaking language question and get SqlQuery, SqlResult and Naturally understandable answers. I have used a few concepts like sequentialChain to connect these inputs and outputs.

**Visualization**: I have started with open-source _**Vega (Facebook developed charts)**_. I am feeding their GitHub to create any chart we need based on data input. Sometimes it might be a bar chart or pie chart. This will be derived based on data input. Also i have experimented with another external charts like _**Highchart**_ where there is api documentation avaiable to utilise and create graphs. We can extend further to add future steps. 

[![IMAGE ALT TEXT](http://img.youtube.com/vi/l5KkqJPqM7I/0.jpg)](https://youtu.be/l5KkqJPqM7I "DataExplore Demo")
https://youtu.be/l5KkqJPqM7I