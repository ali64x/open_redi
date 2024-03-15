#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <regex>

using namespace std;

// Function to process a chunk of data and return the filtered URLs

vector<string> processChunk(const string& chunk) {
    vector<string> chunkURLs;
    regex urlRegex(R"(\bhttps?://\S+\b)");

    sregex_iterator iter(chunk.begin(), chunk.end(), urlRegex);
    sregex_iterator end;

    while (iter != end) {
        string url = iter->str(0);
        chunkURLs.push_back(url);
        ++iter;
    }

    return chunkURLs;
}

void copyFile(const std::string& inputFilename, const std::string& outputFilename) {
    std::ifstream inputFile(inputFilename, std::ios::binary);
    std::ofstream outputFile(outputFilename, std::ios::binary);

    if (!inputFile.is_open()) {
        std::cerr << "Error: Unable to open input file: " << inputFilename << std::endl;
        return;
    }
    if (!outputFile.is_open()) {
        std::cerr << "Error: Unable to open output file: " << outputFilename << std::endl;
        return;
    }

    // Set the buffer size (e.g., 4 KB)
    const size_t bufferSize = 4096;
    std::vector<char> buffer(bufferSize);

    while (!inputFile.eof()) {
        // Read a chunk of data from the input file
        inputFile.read(buffer.data(), bufferSize);
        
        // Get the number of bytes read
        size_t bytesRead = inputFile.gcount();
        
        // Write the data to the output file
        outputFile.write(buffer.data(), bytesRead);
    }

    // Close the files
    inputFile.close();
    outputFile.close();

    std::cout << "File copied successfully." << std::endl;
}

// Function to process the file and return filtered URLs
vector<string> processFile(const string& fileName) {
    ifstream inputFile(fileName);
    vector<string> filteredURLs;

    if (!inputFile.is_open()) {
        cerr << "Error opening input file: " << fileName << endl;
        return filteredURLs;
    }

    string chunk;

    while (getline(inputFile, chunk)) {
        vector<string> chunkURLs = processChunk(chunk);
        for (const auto& url : chunkURLs) {
            if (url.find('?') != string::npos) {
            filteredURLs.push_back(url);
            }
        }
    }

    inputFile.close();
    return filteredURLs;
}

int main(int argc, char* argv[]) {
    if (argc != 2) {
        cerr << "Usage: " << argv[0] << " <input_file>" << endl;
        return 1;
    }

    string inputFileName = argv[1];
    // string outputFileName = argv[2];
    string temp_file =  inputFileName + "/../temp.txt";

    vector<string> filteredURLs = processFile(inputFileName);

    ofstream outputFile(temp_file);
    if (!outputFile.is_open()) {
        cerr << "Error opening output file: " << inputFileName << endl;
        return 1;
    }

    // Write filtered URLs to the output file
    for (const auto& url : filteredURLs) {
        outputFile << url << endl;
    }
    outputFile.close();
    copyFile(temp_file, inputFileName);
    cout << "URLs Filtered Succesfully " << endl;

    return 0;
}
