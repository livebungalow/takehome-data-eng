pragma table_info('real_estate_gold');
/*
0	id				TEXT	0		0
1	listing_type	TEXT	0		0
2	source			TEXT	0		0
3	home_status		TEXT	0		0
4	market			TEXT	0		0
5	home_type		TEXT	0		0
6	address			TEXT	0		0
7	city			TEXT	0		0
8	postal			TEXT	0		0
9	region			TEXT	0		0
10	price			REAL	0		0
11	sqft			REAL	0		0
12	beds			REAL	0		0
13	baths			REAL	0		0
14	year_built		TEXT	0		0
15	load_ts			TEXT	0		0*/

------------------------------------------TOTAL RECORDS----------------------------------------------------------------------------
SELECT count(*) from real_estate_gold
/*
 83791
 */

----------------------------------------------#RENTAL & SALES LISTINGS------------------------------------------------------------
 SELECT listing_type,count(*)
   FROM real_estate_gold
  GROUP BY listing_type 
/*
listing_type	count(*)
ForRent	44338
ForSale	39452
OTHER	1
*/

-----------------------------------------------# RENT & SALES LISTINGS ON EACH MARKET----------------------------------------------
 SELECT market,
        sum(CASE WHEN listing_type = 'ForRent' THEN 1 ELSE 0 END) as rental_listings,
		sum(CASE WHEN listing_type = 'ForSale' THEN 1 ELSE 0 END) as sales_listings
   FROM real_estate_gold		
  GROUP BY market  
/*
    market	rental_listings	sales_listings
	atlanta	 		265		1836
	austin			1809	820
	baltimore		1923	329
	bayarea			7349	1578
	boston			2273	652
	charlotte		0		710
	chicago			2535	3424
	dallas			1908	2191
	denver			414		1395
	houston			0		2870
	lasvegas		0		1068
	losangeles		4513	4036
	miami			361		2880
	nashville			0	639
	newyork			3540	0
	newyorkcity		0		5175
	orangecounty	2399	0
	orlando			0		743
	philadelphia	3644	708
	phoenix			0		1370
	portland		1851	1092
	raleigh			0		481
	saltlakecity	0		423
	sanantonio		1894	1466
	sandiego		3605	995
	seattle			2019	664
	tampa			0		1328
	washington		2036	0
	washingtondc	0		579
*/

----------------------------------------------# RENT & SALES LISTINGS ON EACH REGION/STATE---------------------------------------
 SELECT region,
        sum(CASE WHEN listing_type = 'ForRent' THEN 1 ELSE 0 END) as rental_listings,
		sum(CASE WHEN listing_type = 'ForSale' THEN 1 ELSE 0 END) as sales_listings
   FROM real_estate_gold		
  GROUP BY region  
/*
	region	rental_listings	sales_listings
				0			4
				1411		0
	AZ			0			1370
	CA			17484		6608
	CO			414			1391
	DC			1235		227
	FL			361			4951
	GA			265			1836
	IL			2296		3424
	MA			2056		652
	MD			2091		526
	NC			0			1190
	NJ			1119		365
	NV			0			1068
	NY			2410		3960
	OH			0			3
	OR			1613		1092
	OT			0			1
	PA			3339		708
	SC			0			1
	TN			0			639
	TX			5548		7347
	UT			0			423
	VA			574			152
	WA			2122		1514
*/

------------------------------------------------TOP 5 MOST EXPENSIVE RENTAL UNITS ON EACH MARKET------------------------------------------------------------
SELECT 	* 
FROM (
	SELECT dense_rank() OVER ( PARTITION BY market ORDER BY price DESC	) rank ,
		ID,price,region,home_status,sqft,beds,baths,
		market,source
	FROM
		real_estate_gold
	WHERE listing_type = 'ForRent'
) 
WHERE rank <= 5
--LIMIT 20
/*
rank	ID	price	region	home_status	sqft	beds	baths	market	source
1	2914704	11000.0	GA	Active	3250.0	4.0	4.0	atlanta	zillow
2	2922595	9500.0	GA	Active	1700.0	3.0	2.0	atlanta	zillow
3	2930962	7000.0	GA	Active	2760.0	3.0	2.0	atlanta	zillow
3	2930873	7000.0	GA	Active	2467.0	4.0	3.0	atlanta	zillow
4	2923412	6000.0	GA	Active	1800.0	2.0	2.0	atlanta	zillow
4	2912803	6000.0	GA	Active	2200.0	5.0	4.0	atlanta	zillow
5	2920786	5800.0	GA	Active	3272.0	3.0	3.0	atlanta	zillow
5	2915694	5800.0	GA	Active	2403.0	2.0	2.0	atlanta	zillow
1	2899470	240000.0	TX	Active	1781.0	3.0	3.0	austin	zillow
2	2881021	216000.0	TX	Active	1450.0	3.0	2.0	austin	zillow
3	2904028	15000.0	TX	Active	3000.0	4.0	3.5	austin	zillow
3	2883467	15000.0	TX	Active	3550.0	5.0	5.0	austin	zillow
3	2880522	15000.0	TX	Active	3291.0	4.0	3.0	austin	zillow
4	2880562	14750.0	TX	Active	3100.0	5.0	3.5	austin	zillow
5	2876038	12850.0	TX	Active	3415.0	6.0	3.5	austin	zillow
1	2876379	6600.0	MD	Active	1809.0	5.0	3.0	baltimore	zillow
2	2886787	5500.0	MD	Active	2084.0	5.0	3.0	baltimore	zillow
3	2878894	5400.0	MD	Active	1960.0	6.0	2.5	baltimore	zillow
4	2881830	5000.0	MD	Active	5149.0	5.0	5.0	baltimore	zillow
5	2883217	4600.0	MD	Active	2800.0	4.0	4.0	baltimore	zillow
*/

-----------------------------------------TOP 5 MOST EXPENSIVE UNITS FOR SALE ON EACH MARKET----------------------------------
SELECT 	* 
FROM (
	SELECT dense_rank() OVER ( PARTITION BY market ORDER BY price DESC	) rank ,
		ID,price,region,home_status,sqft,beds,baths,
		market,source
	FROM
		real_estate_gold
	WHERE listing_type = 'ForSale'
) 
WHERE rank <= 5
--LIMIT 20
/*
rank	ID	price	region	home_status	sqft	beds	baths	market	source
1	6781839	10500000.0	GA	Active	15500.0	6.0	10.5	atlanta	FMLS
2	6861703	9875000.0	GA	Active	11380.0	6.0	9.0	atlanta	FMLS
3	6829067	9800000.0	GA	Active	33000.0	9.0	15.0	atlanta	FMLS
4	6901018	9500000.0	GA	Active	15200.0	6.0	10.0	atlanta	FMLS
5	6742469	8800000.0	GA	Active	6652.0	4.0	4.5	atlanta	FMLS
1	4161329	8990000.0	TX	Active	5183.0	5.0	6.0	austin	ACTRIS
2	2854364	6500000.0	TX	Active	4548.0	5.0	6.5	austin	ACTRIS
3	4660236	6000000.0	TX	Active	3094.0	4.0	3.0	austin	ACTRIS
4	8783032	5980000.0	TX	Active	6212.0	5.0	4.5	austin	ACTRIS
5	7196547	5900000.0	TX	Active	6584.0	6.0	7.5	austin	ACTRIS
1	MDHW295512	1750000.0	MD	Active	10072.0	7.0	5.5	baltimore	BRIGHT MLS
2	MDBC519836	1735000.0	MD	Active	6090.0	7.0	6.5	baltimore	BRIGHT MLS
3	MDBC530032	1725000.0	MD	Active	4148.0	5.0	4.5	baltimore	BRIGHT MLS
4	MDBC527730	1625000.0	MD	Active	4969.0	5.0	4.5	baltimore	BRIGHT MLS
5	MDBA547410	1600000.0	MD	Active	6880.0	8.0	9.0	baltimore	BRIGHT MLS
1	421532605	46000000.0	CA	Active	12200.0	6.0	8.0	bayarea	San Francisco MLS
2	ML81846399	30000000.0	CA	Active	10297.0	5.0	5.5	bayarea	MLSListings
3	509969	29500000.0	CA	Active	20000.0	8.0	13.0	bayarea	San Francisco MLS
4	421523154	28000000.0	CA	Active	10345.0	8.0	8.5	bayarea	San Francisco MLS
5	40953497	25800000.0	CA	Active	10734.0	8.0	7.0	bayarea	bridgeMLS, Bay East AOR, or Contra Costa AOR
*/

--------------------------------------------TOP 5 LEAST EXPENSIVE PROPERTIES FOR SALE ON EACH MARKET----------------------------
SELECT 	* 
FROM (
	SELECT dense_rank() OVER ( PARTITION BY market ORDER BY price ASC	) rank ,
		ID,price,region,home_status,sqft,beds,baths,
		market,source
	FROM
		real_estate_gold
	WHERE listing_type = 'ForSale'
) 
WHERE rank <= 5
LIMIT 20
/*
rank	ID	price	region	home_status	sqft	beds	baths	market	source
1	6767998	65000.0		GA	Active				1.0		1.0		atlanta	FMLS
2	6857696	79900.0		GA	Active		800.0	2.0		1.0	atlanta	FMLS
3	6874920	80000.0		GA	Active		1000.0	3.0		1.0	atlanta	FMLS
4	6901240	85000.0		GA	Active				3.0		1.0	atlanta	FMLS
5	6900229	98000.0		GA	Active				0.0		atlanta	FMLS
1	3406099	170000.0	TX	Active	1246.0	3.0	1.0	austin	ACTRIS
2	439246	195000.0	TX	Active	925.0	2.0	1.0	austin	CTXMLS
3	443171	208500.0	TX	Active	1390.0			austin	CTXMLS
4	7190082	220000.0	TX	Active	1289.0	3.0	1.0	austin	ACTRIS
4	442846	220000.0	TX	Active	1202.0	3.0	2.0	austin	CTXMLS
5	9770641	225900.0	TX	Active	1500.0	4.0	2.0	austin	ACTRIS
1	MDBA2000834	25000.0	MD	Active	1576.0	3.0	2.0	baltimore	BRIGHT MLS
2	MDBA2000536	30000.0	MD	Active		3.0	1.5	baltimore	BRIGHT MLS
3	MDBA553108	35000.0	MD	Active	1104.0			baltimore	BRIGHT MLS
3	MDBA551662	35000.0	MD	Active	1450.0			baltimore	BRIGHT MLS
4	MDBA551520	38000.0	MD	Active		2.0	1.5	baltimore	BRIGHT MLS
5	MDBA547674	50000.0	MD	Active				baltimore	BRIGHT MLS
1	421553688	3500.0	CA	Active	1400.0	3.0		bayarea	San Francisco MLS
2	448709	110000.0	OT	Active	900.0	2.0	1.0	bayarea	BNYMLS
3	IN21081091	120000.0	CA	Active	2000.0	0.0		bayarea	CRMLS
*/

---------------------------------------------------------TOP 5 LEAST EXPENSIVE RENTAL UNITS ON EACH MARKET-------------------------
SELECT 	* 
FROM (
	SELECT dense_rank() OVER ( PARTITION BY market ORDER BY price ASC	) rank ,
		ID,price,region,home_status,sqft,beds,baths,
		market,source
	FROM
		real_estate_gold
	WHERE listing_type = 'ForRent'
) 
WHERE rank <= 5
LIMIT 20
/*
rank	ID	price	region	home_status	sqft	beds	baths	market	source
1	2913714	900.0		GA	Active		620.0	2.0		1.0	atlanta		zillow
2	2914705	975.0		GA	Active		1662.0	2.0		1.0	atlanta		zillow
3	2920671	1050.0		GA	Active		1093.0	3.0		2.0	atlanta		zillow
4	2915632	1119.0		GA	Active				2.0		2.0	atlanta		zillow
5	2914579	1125.0		GA	Active		956.0	2.0		1.0	atlanta		zillow
1	2864844	650.0		TX	Active		270.0	0.0		1.0	austin		zillow
2	2866434	800.0		TX	Active		525.0	1.0		1.0	austin		zillow
3	2872069	825.0		TX	Active		430.0	1.0		1.0	austin		zillow
4	2874133	829.0		Active		1.0	1.0	austin	zillow
4	2870743	829.0	TX	Active		1.0	1.0	austin	zillow
5	2872751	850.0	TX	Active	594.0	1.0	1.0	austin	zillow
5	2864832	850.0	TX	Active	650.0	2.0	1.0	austin	zillow
1	2865340	125.0	MD	Active		0.0	1.0	baltimore	zillow
2	2926810	200.0	MD	Active	1200.0	3.0	1.0	baltimore	zillow
3	2870502	500.0	MD	Active			1.0	baltimore	zillow
4	2874543	625.0		Active		1.0	1.0	baltimore	zillow
5	2874537	650.0		Active	420.0		1.0	baltimore	zillow
1	2864988	110.0	CA	Active	709.0	1.0	1.0	bayarea	zillow
2	2877436	650.0	CA	Active	1050.0	3.0	2.0	bayarea	zillow
2	2869856	650.0	CA	Active		0.0		bayarea	zillow
*/

-----------------------------------------------------AVERAGE PRICE OF PROPERTIES - REGION WISE----------------------------------------------
SELECT region,round(avg(price)) as average_price
  FROM real_estate_gold
 WHERE listing_type = 'ForSale'
 GROUP BY region 
 ORDER by average_price
/*
region	average_price
	OT	110000.0
	OH	281600.0
	SC	450000.0
	PA	552603.0
	IL	573228.0
	TX	663520.0
	NC	707093.0
	NV	707739.0
	UT	785325.0
	OR	794715.0
	MD	821562.0
	AZ	838657.0
	GA	887750.0
	CO	911781.0
	NJ	947002.0
	FL	1086229.0
	TN	1091236.0
	NY	1179275.0
	WA	1225426.0
	VA	1479536.0
		1584975.0
	MA	1853912.0
	CA	2469055.0
	DC	2515551.0
*/

--------------------------------------------------------AVG RENT - REGION WISE-----------------------------------------------------------

SELECT region,round(avg(price)) as average_price
  FROM real_estate_gold
 WHERE listing_type = 'ForRent'
 GROUP BY region 
 ORDER by average_price
/*
region	average_price
	MD	1765.0
	PA	1871.0
	IL	1965.0
	OR	2035.0
	TX	2227.0
		2363.0
	NJ	2371.0
	CO	2375.0
	GA	2438.0
	WA	2832.0
	NY	3037.0
	VA	3139.0
	DC	3398.0
	CA	3855.0
	MA	4126.0
	FL	5190.0
*/ 