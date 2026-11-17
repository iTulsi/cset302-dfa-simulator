#include <array>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

// Read a whole line so malformed values such as 2abc cannot slip through.
int readInteger(const std::string& prompt, int minimum, int maximum) {
    std::cout << prompt;
    std::string line;
    if (!std::getline(std::cin, line)) {
        throw std::runtime_error("Unexpected end of input.");
    }
    std::istringstream parser(line);
    int value = 0;
    char extra = '\0';
    if (!(parser >> value) || (parser >> extra) || value < minimum || value > maximum) {
        throw std::runtime_error("Expected an integer from " + std::to_string(minimum) +
                                 " to " + std::to_string(maximum) + ".");
    }
    return value;
}

int main() {
    try {
        std::cout << "DFA Simulator | CSET302\nEnter each answer on a separate line.\n";
        // A classroom resource bound, not a mathematical restriction on DFAs.
        const int stateCount = readInteger("Number of states (1-1000): ", 1, 1000);
        std::cout << "Alphabet (unique printable ASCII symbols, no spaces): ";
        std::string alphabet;
        if (!std::getline(std::cin, alphabet)) {
            throw std::runtime_error("Unexpected end of input.");
        }
        if (alphabet.empty() || alphabet.size() > 94) {
            throw std::runtime_error("Alphabet must contain 1-94 symbols.");
        }
        std::array<int, 256> symbolIndex;
        symbolIndex.fill(-1);
        for (std::size_t i = 0; i < alphabet.size(); ++i) {
            const auto symbol = static_cast<unsigned char>(alphabet[i]);
            if (symbol < 33 || symbol > 126 || symbolIndex[symbol] != -1) {
                throw std::runtime_error("Alphabet symbols must be unique printable ASCII without spaces.");
            }
            symbolIndex[symbol] = static_cast<int>(i);
        }

        std::vector<std::vector<int>> transition(
            stateCount, std::vector<int>(alphabet.size()));
        std::cout << "States are numbered 0 to " << stateCount - 1 << ".\n";
        for (int state = 0; state < stateCount; ++state) {
            for (std::size_t i = 0; i < alphabet.size(); ++i) {
                transition[state][i] = readInteger(
                    "From q" + std::to_string(state) + " on '" + alphabet[i] + "': ",
                    0, stateCount - 1);
            }
        }
        const int startState = readInteger("Start state: ", 0, stateCount - 1);
        const int finalCount = readInteger("Number of final states: ", 0, stateCount);
        std::vector<bool> isFinal(stateCount, false);
        for (int i = 0; i < finalCount; ++i) {
            const int state = readInteger("Final state: ", 0, stateCount - 1);
            if (isFinal[state]) {
                throw std::runtime_error("Duplicate final state.");
            }
            isFinal[state] = true;
        }

        std::cout << "\n--- DFA definition ---\nState";
        for (char symbol : alphabet) std::cout << '\t' << symbol;
        std::cout << "\tStart\tFinal\n";
        for (int state = 0; state < stateCount; ++state) {
            std::cout << 'q' << state;
            for (int next : transition[state]) std::cout << "\tq" << next;
            std::cout << '\t' << (state == startState ? "yes" : "no")
                      << '\t' << (isFinal[state] ? "yes" : "no") << '\n';
        }

        while (true) {
            std::cout << "\nInput string (blank line = epsilon): ";
            std::string input;
            if (!std::getline(std::cin, input)) {
                throw std::runtime_error("Unexpected end of input.");
            }
            int currentState = startState; // Reset for every new test string.
            bool valid = true;
            std::cout << "\n--- Simulation ---\nInput: "
                      << (input.empty() ? "epsilon" : input) << "\nStart: q" << currentState << '\n';
            for (std::size_t i = 0; i < input.size(); ++i) {
                const int index = symbolIndex[static_cast<unsigned char>(input[i])];
                if (index == -1) {
                    std::cout << "Invalid symbol at position " << i + 1
                              << ". Input is outside Sigma*.\n";
                    valid = false;
                    break;
                }
                const int next = transition[currentState][index];
                std::cout << 'q' << currentState << " --" << input[i] << "--> q" << next << '\n';
                currentState = next;
            }
            if (valid) {
                std::cout << "Final state reached: q" << currentState << '\n';
                std::cout << "Result: " << (isFinal[currentState] ? "ACCEPTED" : "REJECTED") << '\n';
            } else {
                std::cout << "Result: INVALID INPUT\n";
            }
            std::cout << "Test another string? (y/n): ";
            std::string answer;
            if (!std::getline(std::cin, answer)) {
                throw std::runtime_error("Unexpected end of input.");
            }
            if (answer == "n" || answer == "N") break;
            if (answer != "y" && answer != "Y") {
                throw std::runtime_error("Expected y or n.");
            }
        }
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "Configuration/input error: " << error.what() << '\n';
        return 1;
    }
}
