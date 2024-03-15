#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <cstdlib>

void mergeFiles(const std::vector<std::string>& fileNames, const std::string& outputFileName) {
    std::ofstream outputFile(outputFileName, std::ios::binary);
    if (!outputFile.is_open()) {
        std::cerr << "Error opening output file." << std::endl;
        return;
    }

    for (const std::string& fileName : fileNames) {
        std::ifstream inputFile(fileName, std::ios::binary);
        if (!inputFile.is_open()) {
            std::cerr << "Error opening input file: " << fileName << std::endl;
            continue;
        }

        // Read and write in chunks
        constexpr size_t bufferSize = 4096; // Adjust buffer size according to your needs
        std::vector<char> buffer(bufferSize);
        while (inputFile.read(buffer.data(), bufferSize)) {
            outputFile.write(buffer.data(), inputFile.gcount());
        }

        // Write any remaining bytes
        outputFile.write(buffer.data(), inputFile.gcount());

        inputFile.close();
    }

    outputFile.close();
    std::cout << "Files merged successfully." << std::endl;
}

int main(int argc, char* argv[]) {
    if (argc < 4) {
        std::cerr << "Usage: " << argv[0] << " -o <output_file> <input_file1> <input_file2> ... <input_fileN>" << std::endl;
        return 1;
    }

    std::vector<std::string> fileNames;
    std::string outputFileName;

    // Parse command-line arguments
    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg == "-o") {
            if (i + 1 < argc) {
                outputFileName = argv[++i];
            } else {
                std::cerr << "Error: Missing output file name after -o flag." << std::endl;
                return 1;
            }
        } else {
            fileNames.push_back(arg);
        }
    }

    // Check if output file name is provided
    if (outputFileName.empty()) {
        std::cerr << "Error: Output file name not provided." << std::endl;
        return 1;
    }

    mergeFiles(fileNames, outputFileName);

    return 0;
}
