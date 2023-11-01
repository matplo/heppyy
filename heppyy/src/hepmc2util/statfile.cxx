#include "statfile.hh"
#include "readfile.hh"

#include <iostream>
#include <fstream>
#include <string>
#include <sstream>

namespace HeppyyHepMCUtil
{
	int statfile(const char *fname, bool quiet)
	{
		std::cout << "[i] reading from " << fname << std::endl;
		HeppyyHepMCUtil::ReadHepMCFile f(fname);
		int nevents = 0;
		while (f.NextEvent())
		{
			if (!quiet) std::cout << " - number of particles:" << f.HepMCParticles(false).size() << std::endl;
			if (!quiet) std::cout << " - number of final particles:" << f.HepMCParticles(true).size() << std::endl;
			nevents++;
		}
		if (!quiet) std::cout << "[i] number of events read: " << nevents << std::endl;
		return nevents;
	};

	int getLastIntegerFromLastNonEmptyLine(const std::string& filename) {
		std::ifstream file(filename);
		std::string line;
		std::string lastNonEmptyLine;

		// Read all lines and find the last non-empty one
		while (std::getline(file, line)) {
			if (!line.empty()) {
				lastNonEmptyLine = line;
			}
		}

		// Extract the integer from the last non-empty line
		std::stringstream ss(lastNonEmptyLine);
		int value;
		ss >> value;

		return value;
	}

	bool fileExists(const std::string& filename) {
		std::ifstream file(filename);
		return file.good();
	}

	void writeIntegerToFile(const std::string& filename, int value) {
		std::ofstream file(filename);

		if (file.is_open()) {
			file << value << std::endl;
			file.close();
		} else {
			std::cerr << "Failed to open the file for writing." << std::endl;
		}
	}

    int get_n_events(const char *fname)
	{
		int nevents = -1;
		const std::string filename = std::string(fname) + std::string(".event_count");
		if (fileExists(filename)) 
		{
			nevents = getLastIntegerFromLastNonEmptyLine(filename);
		} 
		else 
		{
			nevents = statfile(fname);
			writeIntegerToFile(filename, nevents);
		}
		return nevents;		
	}
}