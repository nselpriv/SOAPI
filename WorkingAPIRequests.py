'''

This file contains a list of working endpoints with API requests that may be used in engineering attacks.

----------------------------------------------------------------------

Endpoint GET search/restaurants/{tenant}

curl -X GET "https://uk.api.just-eat.io/search/restaurants/uk?searchTerm=London&latlong=51.5074,-0.1278"

https://uk.api.just-eat.io/search/restaurants/uk?searchTerm=London&latlong=51.5074,-0.1278

This produces list of all restaurants in London around the coordinates

----------------------------------------------------------------------

Endpoint GET restaurants/{tenant}/{restaurantId}/servicetimes

curl -X GET "https://uk.api.just-eat.io/restaurants/uk/72614/servicetimes"

This endpoint gives "Authentication required". It does however seem that in the legacy docs this endpoint was not protected at all

----------------------------------------------------------------------

Endpoint GET restaurants/bypostcode/{postcode}

curl -X GET "https://uk.api.just-eat.io/restaurants/bypostcode/ar511aa"

https://uk.api.just-eat.io/restaurants/bypostcode/ar511aa

This endpoint is referenced from https://github.com/justeat/JustEat.RecruitmentTest/blob/main/Tech.Associate.Engineer.md
It provides a list of sample restaurants used for testing, here we can grab ID's to test

----------------------------------------------------------------------


DK WETBSITE, DOESNT WORK, NEEDS ACCEPT TENANT SMTHN
curl -X GET "https://i18n.api.just-eat.io/restaurants/bypostcode/2300" -H "Accept-Tenant: dk"


'''