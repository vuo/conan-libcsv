#include <stdio.h>
#include <csv.h>

int main()
{
	struct csv_parser parser;
	int ret = csv_init(&parser, CSV_APPEND_NULL);
	if (ret)
	{
		printf("Couldn't initialize libusb.\n");
		return -1;
	}

	printf("Successfully initialized libcsv.\n");
	return 0;
}
