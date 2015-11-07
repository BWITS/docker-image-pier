
CREATE database regsitry;


CREATE TABLE `version` (  
  `id` int(11) NOT NULL AUTO_INCREMENT, 
  `description`  varchar(30),  
  PRIMARY KEY (`id`)  
);  



CREATE TABLE `repository` (  
  `id` int(11) NOT NULL AUTO_INCREMENT,  
  `name` varchar(95) NOT NULL,
  `description`  varchar(30),  
  PRIMARY KEY (`id`)
);  



CREATE TABLE `layer` (  
  `id` int(11) NOT NULL AUTO_INCREMENT,  
  `name` varchar(95) NOT NULL,
  `cnt` varchar(64) NOT NULL,
  `description`  varchar(30),  
  PRIMARY KEY (`id`)
);  


CREATE TABLE `tag` (  
  `id` int(11) NOT NULL AUTO_INCREMENT,  
  `namespace` varchar(95) NOT NULL,
  `imagename` varchar(95) NOT NULL,
  `tagname` varchar(95) NOT NULL,
  `value` varchar(95) NOT NULL,
  `description`  varchar(30),  
  PRIMARY KEY (`id`)
);  

commit;

