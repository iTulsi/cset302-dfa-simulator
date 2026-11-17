#include <iostream>
#include <string>
#include <vector>

using namespace std;

int main() {
    int numberOfStates;
    cout << "Enter number of states: ";
    cin >> numberOfStates;

    if (numberOfStates <= 0) {
        cout << "Invalid number of states.\n";
        return 1;
    }

    string alphabet;
    cout << "Enter alphabet symbols without spaces (example: 01): ";
    cin >> alphabet;

    if (alphabet.empty()) {
        cout << "Alphabet cannot be empty.\n";
        return 1;
    }

    // transition[state][symbolIndex] stores the next state.
    vector<vector<int>> transition(
        numberOfStates,
        vector<int>(alphabet.size())
    );

    cout << "\nEnter the transition table.\n";
    cout << "States are numbered from 0 to " << numberOfStates - 1 << ".\n\n";

    for (int state = 0; state < numberOfStates; ++state) {
        for (int symbolIndex = 0;
             symbolIndex < static_cast<int>(alphabet.size());
             ++symbolIndex) {
            cout << "From state " << state
                 << " on symbol '" << alphabet[symbolIndex]
                 << "', go to state: ";
            cin >> transition[state][symbolIndex];

            if (transition[state][symbolIndex] < 0 ||
                transition[state][symbolIndex] >= numberOfStates) {
                cout << "Invalid next state.\n";
                return 1;
            }
        }
    }

    int startState;
    cout << "\nEnter start state: ";
    cin >> startState;

    if (startState < 0 || startState >= numberOfStates) {
        cout << "Invalid start state.\n";
        return 1;
    }

    int numberOfFinalStates;
    cout << "Enter number of final states: ";
    cin >> numberOfFinalStates;

    if (numberOfFinalStates < 0 || numberOfFinalStates > numberOfStates) {
        cout << "Invalid number of final states.\n";
        return 1;
    }

    vector<bool> isFinalState(numberOfStates, false);
    cout << "Enter final state(s): ";

    for (int i = 0; i < numberOfFinalStates; ++i) {
        int finalState;
        cin >> finalState;

        if (finalState < 0 || finalState >= numberOfStates) {
            cout << "Invalid final state.\n";
            return 1;
        }

        isFinalState[finalState] = true;
    }

    string input;
    cout << "Enter input string: ";
    cin >> input;

    int currentState = startState;

    cout << "\n--- Simulation ---\n";
    cout << "Start at state " << currentState << "\n";

    for (char symbol : input) {
        size_t symbolIndex = alphabet.find(symbol);

        if (symbolIndex == string::npos) {
            cout << "Symbol '" << symbol << "' is not in the alphabet.\n";
            cout << "Result: REJECTED\n";
            return 0;
        }

        int nextState = transition[currentState][symbolIndex];

        cout << currentState << " --" << symbol << "--> " << nextState << "\n";
        currentState = nextState;
    }

    cout << "Final state reached: " << currentState << "\n";

    if (isFinalState[currentState]) {
        cout << "Result: ACCEPTED\n";
    } else {
        cout << "Result: REJECTED\n";
    }

    return 0;
}
