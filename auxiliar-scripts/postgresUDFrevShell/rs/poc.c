#include "postgres.h"
#include <string.h>
#include "fmgr.h"
#include "utils/geo_decls.h"
#include <stdio.h>
#include "utils/builtins.h"

#ifdef PG_MODULE_MAGIC
PG_MODULE_MAGIC;
#endif

/* Add a prototype marked PGDLLEXPORT */
PGDLLEXPORT Datum system(PG_FUNCTION_ARGS);
PG_FUNCTION_INFO_V1(system);

Datum
system(PG_FUNCTION_ARGS)
{
	/* convert C string to text pointer */
#define GET_TEXT(cstrp) \
    DatumGetTextP(DirectFunctionCall1(textin, CStringGetDatum(cstrp)))

	/* convert text pointer to C string */
#define GET_STR(textp) \
    DatumGetCString(DirectFunctionCall1(textout, PointerGetDatum(textp)))

	// do something
	GET_STR(PG_GETARG_TEXT_P(0));
	// do something
	PG_RETURN_VOID();
}
