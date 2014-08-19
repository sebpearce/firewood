/**
  * firewood.c
  *
  * Author: Seb Pearce
  *
  * Date: 2014-01-22
  *
  * Parses "My Clippings.txt" & creates a directory of text files based on
  * book titles.
  */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <stdbool.h>
#include <errno.h>
#include <sys/stat.h>

#define DEFAULT_FILENAME "../../../My Clippings.txt"
#define DEFAULT_DIRNAME "../../../Kindle Clippings/"
#define PATH_LENGTH 18
#define TITLE_LENGTH 200
#define CLIPPING_LENGTH 50000

enum {
    TITLE_LINE = 1,
    CLIPPING_INFO = 2,
    BLANK_LINE = 3,
    CLIPPING_TEXT = 4,
    EQUALS_LINE = 5
};

FILE* infile = NULL;
FILE* outfile = NULL;
int tcnt = 0;                       // title counter (++ if new book is found)
char* listoftitles[1000] = {NULL};  // list of pointers to book titles

// die function in case something goes wrong
void die(const char *message)
{
    // close open files
    if (infile) fclose(infile);
    if (outfile) fclose(outfile);
    // free title array space
    for (int i = 0; i < tcnt; i++) {
        if (listoftitles[i]) free(listoftitles[i]);
    }
    // die and print message
    if (message) {
        printf("%s", message);
    } else {
        printf("Error: could not extract clippings.\n");
    }
    exit(1);
}

// replace trailing \n, \r and space with \0
void trimNewline(char* s)
{
    for (int i = 1; i <= 2; i++) {
        if (s[strlen(s)-i] == '\n') s[strlen(s)-i] = '\0';
        if (s[strlen(s)-i] == '\r') s[strlen(s)-i] = '\0';
    }

    // check for trailing space
    if (s[strlen(s)-1] == ' ') s[strlen(s)-1] = '\0';
}

// create a new file for writing
void openTitle(char* title, const char* action)
{
    // make a temp filename to store the title
    char filename[TITLE_LENGTH] = {0};
    char path[TITLE_LENGTH+PATH_LENGTH] = DEFAULT_DIRNAME;
    strncpy(filename, title, strlen(title));
    filename[strlen(title)] = '\0';
    // trim trailing \n and \r and space from filename
    trimNewline(filename);
    // add .txt
    strcat(filename, ".txt");
    // add rest of path
    strcat(path, filename);

    // open the new outfile
    outfile = fopen(path, action);  
    if (!outfile) {
        die("Error: could not save to file.\n");
    } 
}

int main(void)
{
    // open the My Clippings file
    infile = fopen(DEFAULT_FILENAME, "r");
    if (!infile) {
        die("Error: could not open My Clippings.txt.\n");
    }

    // check if we have the byte order mark (BOM) at the beginning
    uint8_t bytebuf[3] = {0};
    fread(&bytebuf, 1, 3, infile);
    // if it's not there, fseek back to the start
    if (bytebuf[0] != 0xEF || bytebuf[1] != 0xBB || bytebuf[2] != 0xBF) {
        fseek(infile, 0, SEEK_SET);
    }

    // create clippings folder for output
    int mkdirok = mkdir(DEFAULT_DIRNAME, S_IRWXU);
    if (mkdirok != 0) {
        die("Error: could not create Kindle Clippings directory. Please check "
            "that it does not already exist.\n");
    }

    char output[CLIPPING_LENGTH]={0};   // CLIPPING_LENGTH char line buffer
    char title[TITLE_LENGTH]={0};       // title buffer
    char clippingtext[CLIPPING_LENGTH]={0}; // clipping text buffer
    bool oldtitle = false;              // a title we've already encountered
    int section = 1;                    // section counter:
                                        // 1: title line; 2: clipping info;
                                        // 3: blank; 4: clipping text; 5: ====

    // iterate through each line until the end
    while (fgets(output, sizeof(output), infile) != NULL) {

        switch (section) {

            case TITLE_LINE:
                // same title as last time? just print ...
                if (strncmp(title, output, strlen(output)) == 0) {
                    fprintf(outfile, "...\n");
                } else {
                    // first, check if title has already been stored in list
                    for (int i = 0; i < tcnt; i++) {
                        if (strcmp(listoftitles[i], output) == 0) {
                            // store name in title buffer
                            strncpy(title, output, strlen(output));
                            title[strlen(output)] = '\0';
                            oldtitle = true;
                            // close old outfile
                            if (outfile) fclose(outfile);
                            // open old outfile (to append) using same filename
                            openTitle(listoftitles[i], "a");
                            fprintf(outfile, "...\n");
                            break;
                        }
                    }
                    // if the title has changed (i.e. new book)
                    if (oldtitle != true) {
                        // add new title to list
                        listoftitles[tcnt] = calloc(1, sizeof(output) + 1);
                        strncpy(listoftitles[tcnt], output, strlen(output));
                        listoftitles[tcnt][strlen(output)] = '\0';
                        // close last outfile
                        if (outfile) fclose(outfile);
                        // open a new outfile using the title as a filename
                        openTitle(listoftitles[tcnt], "w");
                        tcnt++;
                        // store name in title buffer
                        strncpy(title, output, strlen(output));
                        title[strlen(output)] = '\0';
                        // print the new title to the outfile
                        fprintf(outfile, "%s\n", title);
                    }
                    oldtitle = false;
                }
                break;

            case CLIPPING_INFO:
                // this is the clipping info; just print a newline
                fprintf(outfile, "\n");
                break;

            case BLANK_LINE:
                // skip (blank line)
                break;

            case CLIPPING_TEXT:
                // print the clipping text
                strncpy(clippingtext, output, strlen(output));
                clippingtext[strlen(output)] = '\0';
                fprintf(outfile, "%s", clippingtext);
                break;

            case EQUALS_LINE:
                // this is the ========= line; just print a newline
                fprintf(outfile, "\n");
                section = 0;
                break;
                
            default:
                break;
        }

        section++;      // go to the next line

    }

    // free title array space
    for (int i = 0; i < tcnt; i++) {
        if (listoftitles[i]) free(listoftitles[i]);
    }

    // close open files
    if (infile) fclose(infile);
    if (outfile) fclose(outfile);

    // adios
    return 0;
}
