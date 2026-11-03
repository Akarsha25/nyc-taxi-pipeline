
select * from (values
(0,'Flex fare'),
(1,'Credit Card'),
(2,'Cash'),
(3,'No Charge'),
(4,'Dispute'),
(5,'Unknown'),
(6,'Voided trip')
) as t(payment_type_id,payment_name)
