#pragma once
#include <iostream>
#include <chrono>
#include <vector>

#include <assert.h>
#define assume(x) assert((x))

namespace dbg
{
#ifdef PROFILE
//#define _DBG_INTERNAL_STATIC_BUFFER_SIZE 512

    using namespace std::chrono;
    typedef size_t ID;
    
    struct PRF_global_t
    {
        std::vector<std::string> names;
        std::vector<N64_t>       times;
        std::vector<N>                 hits;
        std::vector<N>                 levels; // NOTE: may remove

        std::vector<dbg::ID> branches;
        N branch_sub       = 0;
        
        dbg::ID current_id = 0;

        dbg::ID last_counter = 0;
        dbg::ID last_id;
        
        PRF_global_t()
        {
            
        }
        
        ~PRF_global_t()
        {
            /* Output */
            if (names.empty()) return;
            
            double time_total = 0.0;
            for (dbg::ID id = 0; id < names.size(); ++ id)
            {
                /* Padding */
                std::string pad_str = "";
                for (N _pad = 0; _pad < levels[id]; ++ _pad)
                {
                    pad_str += " ";
                }

                /* Name */
                std::cout << pad_str << names[id] << ": " << std::endl;

                /* Data */
                double time_ms   = (double)times[id] / 1e6;
                N      hit_count = hits[id];
                time_total += time_ms;
                std::cout << pad_str << " " << time_ms   << " ms"     << std::endl;
                std::cout << pad_str << " " << hit_count << " hit[s]" << std::endl;
                if (hit_count > 1)
                {
                    double avg_time = time_ms / hit_count;
                    std::cout << pad_str << " " << avg_time << "ms/hit" << std::endl;
                }

                /* Final separation */
                std::cout << std::endl;
            }

            /* Total time */
            std::cout << "Total:  " << time_total << " ms" << std::endl;
        }
        
        const dbg::ID add(const size_t counter, const std::string name)
        {
            if (counter == last_counter)
            {
                ++ branch_level;
                return last_id;
            }

            dbg::ID return_id = current_id;
            // To find top level functions
            if (branch_level == 0 && !names.empty())
            {
                for (size_t id = 0; id < names.size(); ++ id)
                {
                    if (name == names[id])
                    {
                        return_id = id;
                    }
                }
            }

            if (return_id == current_id)
            {
                names.push_back(name);
                times.push_back(0);
                hits.push_back(0);
                levels.push_back(branch_level); // NOTE: may remove    
            }
            
            ++ branch_level;
            ++ current_id;
            last_counter = counter;
            last_id      = return_id;
            return return_id;
        }

        void report(dbg::ID id, N64_t t)
        {
            assume(this->times.size() > id);
            assume(this->hits.size() > id);
            assume(this->branch_level > 0);

            times[id] += t - branch_sub;
            ++ hits[id];

            -- branch_level;
            if (branch_level > 0) branch_sub = t;
            else                  branch_sub = 0;
        }
    };
    
    static PRF_global_t _PRF_global = dbg::PRF_global_t();
    struct PRF_local_t
    {
        dbg::ID id;
        high_resolution_clock::time_point t;

        PRF_local_t(const dbg::ID counter, const char * name)
        {
            id = _PRF_global.add(counter, name);
            t = high_resolution_clock::now();
        }

        ~PRF_local_t()
        {
            high_resolution_clock::time_point t2 = high_resolution_clock::now();
            N64_t t_ns = duration_cast<nanoseconds>(t2 - t).count();

            _PRF_global.report(id, t_ns);
        }
    };
    
    
    
#define profile_fn() dbg::PRF_local_t _tmp_profiler__##__COUNTER__(__COUNTER__, __FUNCTION__); // Use COUNTER to get unique object name.
    #ifndef PROFILE_NOBRANCH
#define profile(name) dbg::PRF_local_t _tmp_profiler__##__COUNTER__(__COUNTER__, (name));
    #else
#define profile(name)
    #endif
#define profile_output()/*dbg::_PRF_output();*/
#else
#define profile(name)
#define profile_fn()
#define profile_output()
#endif    
}
