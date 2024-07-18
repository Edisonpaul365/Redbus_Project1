use redbus;

desc bus_route;

select * from routename;
select count(*) from routename;
select * from bus_route;
select count(*) from bus_route;

SELECT DISTINCT b.bus_route_name, a.Route_link
FROM routename a
JOIN bus_route b ON a.Bus_Route_Name = b.bus_route_name;
