#ifndef HEPPYY_HEPMCWRAP_TEST_HH
#define HEPPYY_HEPMCWRAP_TEST_HH

namespace HeppyyHepMCUtil
{
    int statfile(const char *fname, bool quiet=true);
    int get_n_events(const char *fname);
};
#endif