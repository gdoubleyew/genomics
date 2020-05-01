#include <iostream>
#include <fstream>
#include <sstream> //stringstream
#include <map>
#include <vector>
#include <chrono>
#include <getopt.h>
#include <regex>
#include <cstdio>

#ifdef __linux__
  #include <experimental/filesystem>
  namespace fs = std::experimental::filesystem;
#elif __APPLE__
  #include <filesystem>
  namespace fs = std::__fs::filesystem;
#endif

using namespace std;
using namespace std::chrono;

string baseDir = "/tmp/files";
string fileBaseName = "test";
int verbose = 0;

bool create_file(const string &strFilename, const string &text, const size_t size=0) {
  fstream fp;
  fp.open(strFilename.c_str(), ios_base::out);
  if (!fp.is_open()) {
    return false;
  }
  if (size > 0) {
    fp.seekp(size);
  }
  fp.write((char *) text.c_str(), text.size());
  fp.close();
  return true;
}

bool append_file(const string &strFilename, const string &text) {
  fstream fp;
  fp.open(strFilename.c_str(), ios_base::out | ios_base::app);
  if (!fp.is_open()) {
    return false;
  }
  fp.write((char *) text.c_str(), text.size());
  fp.close();
  return true;
}

bool read_file(const string &strFilename, string &result) {
  stringstream strStream;
  ifstream inFile;
  inFile.exceptions ( ifstream::badbit | ifstream::failbit );
  inFile.open(strFilename.c_str());
  if (! inFile) {
    return false;
  }
  strStream << inFile.rdbuf();
  result = strStream.str();
  return true;
}

// Top Level Functions to perform operations on vector of filenames
void create_files(vector<string> &fileNames) {
  cout << "Create Files:" << endl;
  for (auto fileName : fileNames) {
    string text = "Text for " + fileName + '\n';
    create_file(fileName, text);
  }
  return;
}

void create_sparse_files(vector<string> &fileNames, size_t size) {
  cout << "Create Sparse Files:" << endl;
  for (auto fileName : fileNames) {
    string text = "Text for " + fileName + '\n';
    create_file(fileName, text, size);
  }
  return;
}

void append_files(vector<string> &fileNames, int append_id) {
  cout << "Append Files:" << endl;
  for (auto fileName : fileNames) {
    string text = "append " + to_string(append_id) + '\n';
    append_file(fileName, text);
  }
  return;
}

bool append_already_open(vector<string> &fileNames, int append_id) {
  cout << "Append Open:" << endl;
  string text = "append " + to_string(append_id) + '\n';
  fstream fp;
  fp.open(fileNames[0].c_str(), ios_base::out | ios_base::app);
  if (!fp.is_open()) {
    return false;
  }
  for (auto fileName : fileNames) {
    fp.write((char *) text.c_str(), text.size());
  }
  fp.close();
  return true;
}

void read_files(vector<string> &fileNames) {
  cout << "Read Files:" << endl;
  for (auto fileName : fileNames) {
    string content;
    bool res = read_file(fileName, content);
    if (!res) {
      cout << "missing file " << fileName << endl;
    } else if (verbose) {
        cout << content << endl;
    }
  }
}

int create_flag = 0;
int create_sparse_flag = 0;
int append_flag = 0;
int append_open_flag = 0;
int read_flag = 0;
int rm_flag = 0;

static struct option long_options[] =
{
  {"create", 0, &create_flag, 1},
  {"create_sparse", 0, &create_sparse_flag, 1},
  {"append", 0, &append_flag, 1},
  {"append_open", 0, &append_open_flag, 1},
  {"read", 0, &read_flag, 1},
  {"rm", 0, &rm_flag, 1},

  {"verbose", 0, &verbose, 1},
  {0, 0, 0, 0}
};

int main(int argc, char** argv) {
  int numFiles = 0;
  int sparseSize = 0;
  while(true) {
    int idx = 0;
    int c = getopt_long (argc, argv, "n:s:", long_options, &idx);
    if (c == -1) {
      break;
    }
    switch(c) {
      case 0:
        /* longopts flags automatically handled */
        break;
      case 'n':
        numFiles = atol(optarg);
        break;
      case 's':
        sparseSize = atol(optarg);
        break;
      default:
        cout << "unrecognized option " << c << endl;
        exit(-1);
    }
  }

  vector<string> fileNames;
  for (int i = 0; i < numFiles; i++) {
    string fileName = baseDir + "/" + fileBaseName + to_string(i);
    fileNames.push_back(fileName);
  }

  if (create_flag) {
    auto start = high_resolution_clock::now();
    create_files(fileNames);
    auto duration = duration_cast<microseconds>(high_resolution_clock::now() - start);
    auto timems = duration.count() / 1000.0;
    cout << "Create time: " << timems << " ms" << endl;
  }

  if (create_sparse_flag) {
    auto start = high_resolution_clock::now();
    create_sparse_files(fileNames, sparseSize);
    auto duration = duration_cast<microseconds>(high_resolution_clock::now() - start);
    auto timems = duration.count() / 1000.0;
    cout << "Create time: " << timems << " ms" << endl;
  }

  if (append_flag) {
    auto start = high_resolution_clock::now();
    append_files(fileNames, 1);
    auto duration = duration_cast<microseconds>(high_resolution_clock::now() - start);
    auto timems = duration.count() / 1000.0;
    cout << "Append time: " << timems << " ms" << endl;
  }

  if (append_open_flag) {
    auto start = high_resolution_clock::now();
    append_already_open(fileNames, 1);
    auto duration = duration_cast<microseconds>(high_resolution_clock::now() - start);
    auto timems = duration.count() / 1000.0;
    cout << "Append_open time: " << timems << " ms" << endl;
  }

  if (read_flag) {
    auto start = high_resolution_clock::now();
    read_files(fileNames);
    auto duration = duration_cast<microseconds>(high_resolution_clock::now() - start);
    auto timems = duration.count() / 1000.0;
    cout << "Read time: " << timems << " ms" << endl;
  }

  if (rm_flag) {
    /* remove files from test directory */
    string filePattern = baseDir + "/" + fileBaseName + ".*";
    cout << filePattern << endl;
    regex re(filePattern);
    for (const auto & dirEntry : fs::directory_iterator(baseDir)) {
      string filename = dirEntry.path().string();
      if (regex_match(filename, re)) {
        cout << filename << endl;
        remove(filename.c_str());
      }
    }
  }

}
