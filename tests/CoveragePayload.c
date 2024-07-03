﻿/*
 * SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
 * SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 * Licensed under the Apache License v2.0 with LLVM Exceptions.
 * See LICENSE.txt for license information.
 */

#include <nvtx3/nvToolsExtPayload.h>

void TestMem()
{
    nvtxDomainHandle_t domain;
    uint8_t enabled;
    uint64_t handle;
    nvtxPayloadSchemaAttr_t attr;

    domain = nvtxDomainCreateA("Domain");
    enabled = nvtxDomainIsEnabled(domain);
    handle = nvtxPayloadSchemaRegister(domain, &attr);
}

#include "DllHelper.h"

DLL_EXPORT
int RunTest(int argc, const char** argv)
{
    (void)argc;
    (void)argv;

    TestMem();

    return 0;
}
