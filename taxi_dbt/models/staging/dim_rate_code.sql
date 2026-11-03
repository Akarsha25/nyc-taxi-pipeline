
select * from (values
(1,'Standard rate'),
(2,'JFK airport'),
(3,'Newark airport'),
(4,'Nassau or Westchester'),
(5,'Negotiated fare'),
(6,'Group ride'),
(99,'Unknown') )as t(rate_code_id,rate_name)