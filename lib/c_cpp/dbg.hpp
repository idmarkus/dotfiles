#pragma once
#include <personal/typedefs.h>

#include <iostream>

#include <string.h>
#include <assert.h>
#define assume(x) assert((x))

#define logexpr(x) std::cout << (#x) << ": " << (x) << std::endl;

namespace dbg
{
    
    
#ifdef BENCHMARK
#include <chrono>
#include <vector>

#define BNCH_NAME_BUFFER_SIZE 512

    using namespace std;
    using namespace std::chrono;
    
    struct BENCH_data_t
    {
        const size_t id;
        const size_t depth;
        //size_t branch_ofs = 0;
        N64_t t_ns = 0;
        N64_t hit_count = 0;
        
        BENCH_data_t(const size_t _id, const size_t _depth) : id(_id), depth(_depth)
        {
            
        }
    };
    struct BENCH_t;
    struct BENCH_stack_ptr_t;
    namespace BNCH
    {
        static vector<BENCH_data_t>   branches;
        static vector<BENCH_stack_ptr_t *> branch_stack;
        //static size_t              current_branch = 0;
        static size_t              current_depth  = 0;
        
        static const char * name_lut[BNCH_NAME_BUFFER_SIZE] = {0};

        static constexpr size_t ofs_store = __COUNTER__;
        constexpr size_t id_offset(const size_t n)
        {
            //constexpr int calc = n - ofs_store;
            return n - dbg::BNCH::ofs_store;
        }

        void output()
        {
            N longest_name_length = 0;
            for (size_t i = 0; i < BNCH_NAME_BUFFER_SIZE; ++ i)
            {
                if (name_lut[i] != NULL)
                {
                    N len = strlen(name_lut[i]);
                    if (len > longest_name_length)
                    {
                        longest_name_length = len;
                    }
                }
            }
            
            double total_ms = 0;
            cout << "Benchmark:" << endl << endl;
            for (BENCH_data_t b : branches)
            {
                /* Name padding */
                N name_len = longest_name_length - strlen(name_lut[b.id]) + 1;
                string name_padding = "";
                for (size_t i = 0; i < name_len; ++ i)
                {
                    name_padding += " ";
                }
                
                /* Depth padding */
                string depth_padding = "";
                for (size_t i = 0; i < b.depth; ++ i)
                {
                    depth_padding += " ";
                }
                depth_padding += "└";
                
                /* Name */
                cout << depth_padding << name_lut[b.id] << ": " << name_padding;

                /* Data */
                double t_ms = (double)b.t_ns / 1e6;
                N64_t  hits = b.hit_count;
                cout << t_ms << "ms, ";
                cout << hits << endl;
                if (b.depth == 0)
                    total_ms += t_ms;
            }
            cout << "Total: " << total_ms << " ms" << endl;
        }
    }

    struct BENCH_stack_ptr_t
    {
        const size_t id;
        const size_t depth;
        const size_t ofs;
        vector<size_t> child_id;
        vector<size_t> child_pos;
        BENCH_stack_ptr_t(size_t _id, size_t _depth, size_t _ofs) : id(_id), depth(_depth), ofs(_ofs) {}
    };
    
    struct BENCH_t
    {
        const size_t id;
        size_t ofs;
        vector<size_t> child_id;
        vector<size_t> child_pos;
        high_resolution_clock::time_point t;

        BENCH_t(const size_t _id) : id(_id)
        {
            using namespace BNCH;
            while (!branch_stack.empty() && branch_stack.back()->depth >= current_depth)
            {
                if (branch_stack.back()->id == id)
                {
                    ofs = branch_stack.back()->ofs;
                    ++ current_depth;
                    t = high_resolution_clock::now();
                    return;
                }
                else
                {
                    branch_stack.pop_back();
                }
            }
            
            if (branch_stack.empty())
            {
                branches.push_back(BENCH_data_t(id, current_depth));
                ofs = branches.size() - 1;
            }
            else
            {
                BENCH_stack_ptr_t * parent = branch_stack.back();
                bool found = false;
                if (!parent->child_id.empty())
                {
                    for (size_t id_i = 0; id_i < parent->child_id.size(); ++ id_i)
                    {
                        if (parent->child_id[id_i] == id)
                        {
                            assume(id_i < parent->child_pos.size());
                            ofs = parent->child_pos[id_i];
                            found = true;
                            break;
                        }
                    }
                }
                if (!found)
                {
                    /* Spawn new child */
                    branches.push_back(BENCH_data_t(id, current_depth));
                    ofs = branches.size() - 1;
                    parent->child_pos.push_back(ofs);
                    parent->child_id.push_back(id);
                }
            }

            BENCH_stack_ptr_t * stack_ptr = new BENCH_stack_ptr_t(id, current_depth, ofs);
            branch_stack.push_back(stack_ptr);
            ++ current_depth;
            t = high_resolution_clock::now();
/*
            if (current_branch >= branches.size())
            {
                //Initialise new BNCH_data object
                branches.push_back(BNCH_data_t(id, current_depth));
            }
            else if (branches[current_branch].id != id)
            {
                size_t tmp_branch = current_branch;
                while (branches[current_branch].ofs_fwd != 0)
                {
                    if (branches[current_branch].id == id)
                    {
                        
                    }
                    tmp_branch += branches[tmp_branch].ofs_fwd;
                }
                //Initialise new BNCH_data object
                    branches.push_back(BNCH_data_t(id, current_depth));
                    current_branch              = branches.size() - 1;
                    branches[branch].branch_ofs = current_branch - branch;
                    branch                      = current_branch;    
                }
                else
                {
                    current_branch += branches[current_branch].ofs_fwd;
                }
            }            
            branch = current_branch;
            */
            
        }

        ~BENCH_t()
        {
            using namespace BNCH;
            high_resolution_clock::time_point t2 = high_resolution_clock::now();

            assume(ofs < branches.size());
            
            branches[ofs].t_ns      += duration_cast<nanoseconds>(t2 - t).count();
            branches[ofs].hit_count += 1;
            
            //current_branch = branch;
            -- current_depth;
        }
    };

    struct BNCH_subblock_t
    {
        const size_t super_id;
        const size_t id;
        high_resolution_clock::time_point t;
        
    };
    
    // TODO: fix __FUNCTION__ to add "()" at the end at compile time
#define benchmark_fn()\
    constexpr size_t _BNCH_id = dbg::BNCH::id_offset(__COUNTER__);\
    if (dbg::BNCH::name_lut[_BNCH_id] == 0) dbg::BNCH::name_lut[_BNCH_id] = __FUNCTION__; \
    dbg::BENCH_t _BNCH_obj = dbg::BENCH_t(_BNCH_id);
#define benchmark(NAME)\
    constexpr size_t _BNCH_sub_id = dbg::BNCH::id_offset(__COUNTER__);\
    if (dbg::BNCH::name_lut[_BNCH_sub_id] == 0) dbg::BNCH::name_lut[_BNCH_sub_id] = (NAME); \
    dbg::BENCH_t _BNCH_sub_obj = dbg::BENCH_t(_BNCH_sub_id);
#define benchmark_output() dbg::BNCH::output();
    #else // #ifdef BENCHMARK
#define benchmark_fn()
#define benchmark(NAME)
#define benchmark_output()
    #endif // #ifdef BENCHMARK
}
