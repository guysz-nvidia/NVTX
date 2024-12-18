# SPDX-FileCopyrightText: Copyright (c) 2020-2022 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Licensed under the Apache License v2.0 with LLVM Exceptions.
# See https://nvidia.github.io/NVTX/LICENSE.txt for license information.

import contextlib
import os

from functools import wraps

from nvtx._lib import (
    Domain,
    RegisteredString,
    EventAttributes,
    mark as libnvtx_mark,
    pop_range as libnvtx_pop_range,
    push_range as libnvtx_push_range,
    start_range as libnvtx_start_range,
    end_range as libnvtx_end_range,
)

_ENABLED = not os.getenv("NVTX_DISABLE", False)


class annotate:
    """
    Annotate code ranges using a context manager or a decorator.
    """

    def __init__(self, message=None, color=None, domain=None, category=None, payload=None):
        """
        Annotate a function or a code range.

        Parameters
        ----------
        message : str, optional
            A message associated with the annotated code range.
            When used as a decorator, the default value of message
            is the name of the function being decorated.
            When used as a context manager, the default value is the empty
            string.
            Messages are cached and are registered as Registered Strings
            in NVTX.
            Caching a very large number of messages may lead to increased
            memory usage.
        color : str or color, optional
            A color associated with the annotated code range.
            Supports `matplotlib` colors if it is available.
        domain : str, optional
            A string specifying the domain under which the code range is
            scoped. The default domain is named "NVTX".
        category : str, int, optional
            A string or an integer specifying the category within the domain
            under which the code range is scoped. If unspecified, the code
            range is not associated with a category.
        payload : int or float, optional
            A numeric value to be associated with this event

        Examples
        --------
        >>> import nvtx
        >>> import time

        Using a decorator:

        >>> @nvtx.annotate("my_func", color="red", domain="my_domain")
        ... def func():
        ...     time.sleep(0.1)

        Using a context manager:

        >>> with nvtx.annotate("my_code_range", color="blue"):
        ...    time.sleep(10)
        ...
        """

        self.domain = Domain(domain)
        message = RegisteredString(self.domain.handle, message)

        category_id = None
        if isinstance(category, int):
            category_id = category
        elif isinstance(category, str):
            category_id = self.domain.get_category_id(category)
        self.attributes = EventAttributes(message, color, category_id, payload)

    def __reduce__(self):
        return (
            self.__class__,
            (
                self.attributes.message.string,
                self.attributes.color,
                self.domain.name,
                self.attributes.category,
            ),
        )

    def __enter__(self):
        libnvtx_push_range(self.attributes, self.domain.handle)
        return self

    def __exit__(self, *exc):
        libnvtx_pop_range(self.domain.handle)
        return False

    def __call__(self, func):
        if not self.attributes.message.string:
            self.attributes.message = RegisteredString(
                self.domain.handle, func.__name__
            )

        @wraps(func)
        def inner(*args, **kwargs):
            libnvtx_push_range(self.attributes, self.domain.handle)
            result = func(*args, **kwargs)
            libnvtx_pop_range(self.domain.handle)
            return result

        return inner


def mark(message=None, color="blue", domain=None, category=None, payload=None):
    """
    Mark an instantaneous event.

    Parameters
    ----------
    message : str, optional
        A message associated with the event.
        Messages are cached and are registered as Registered Strings
        in NVTX.
        Caching a very large number of messages may lead to increased
        memory usage.
    color : str, color, optional
        Color associated with the event.
    domain : str, optional
        A string specifuing the domain under which the event is scoped.
        The default domain is named "NVTX".
    category : str, int, optional
        A string or an integer specifying the category within the domain
        under which the event is scoped. If unspecified, the event is
        not associated with a category.
    payload : int or float, optional
            A numeric value to be associated with this event
    """
    domain = Domain(domain)
    message = RegisteredString(domain.handle, message)

    category_id = None
    if isinstance(category, int):
        category_id = category
    elif isinstance(category, str):
        category_id = domain.get_category_id(category)
    attributes = EventAttributes(message, color, category_id, payload)
    libnvtx_mark(attributes, domain.handle)


def push_range(message=None, color="blue", domain=None, category=None, payload=None):
    """
    Mark the beginning of a code range.

    Parameters
    ----------
    message : str, optional
        A message associated with the annotated code range.
        Messages are cached and are registered as Registered Strings
        in NVTX.
        Caching a very large number of messages may lead to increased
        memory usage.
    color : str, color, optional
        A color associated with the annotated code range.
        Supports
    domain : str, optional
        Name of a domain under which the code range is scoped.
        The default domain name is "NVTX".
    category : str, int, optional
        A string or an integer specifying the category within the domain
        under which the code range is scoped. If unspecified, the code range
        is not associated with a category.
    payload : int or float, optional
            A numeric value to be associated with this event

    Examples
    --------
    >>> import time
    >>> import nvtx
    >>> nvtx.push_range("my_code_range", domain="my_domain")
    >>> time.sleep(1)
    >>> nvtx.pop_range(domain="my_domain")
    """
    domain = Domain(domain)
    message = RegisteredString(domain.handle, message)

    category_id = None
    if isinstance(category, int):
        category_id = category
    elif isinstance(category, str):
        category_id = domain.get_category_id(category)
    libnvtx_push_range(EventAttributes(message, color, category_id, payload),
                       domain.handle)


def pop_range(domain=None):
    """
    Mark the end of a code range that was started with `push_range`.

    Parameters
    ----------
    domain : str, optional
        The domain under which the code range is scoped. The default
        domain is "NVTX".
    """
    libnvtx_pop_range(Domain(domain).handle)


def start_range(message=None, color="blue", domain=None, category=None, payload=None):
    """
    Mark the beginning of a code range.

    Parameters
    ----------
    message : str, optional
        A message associated with the annotated code range.
        Messages are cached and are registered as Registered Strings
        in NVTX.
        Caching a very large number of messages may lead to increased
        memory usage.
    color : str, color, optional
        A color associated with the annotated code range.
        Supports
    domain : str, optional
        Name of a domain under which the code range is scoped.
        The default domain name is "NVTX".
    category : str, int, optional
        A string or an integer specifying the category within the domain
        under which the code range is scoped. If unspecified, the code range
        is not associated with a category.
    payload : int or float, optional
            A numeric value to be associated with this event

    Returns
    -------
    An object of type `RangeId` that must be passed to the `end_range()` function.

    Examples
    --------
    >>> import time
    >>> import nvtx
    >>> range_id = nvtx.start_range("my_code_range", domain="my_domain")
    >>> time.sleep(1)
    >>> nvtx.end_range(range_id, domain="my_domain")
    """
    domain = Domain(domain)
    message = RegisteredString(domain.handle, message)

    category_id = None
    if isinstance(category, int):
        category_id = category
    elif isinstance(category, str):
        category_id = domain.get_category_id(category)
    marker_id = libnvtx_start_range(
        EventAttributes(message, color, category_id, payload), domain.handle)
    return marker_id


def end_range(range_id):
    """
    Mark the end of a code range that was started with `start_range`.

    Parameters
    ----------
    range_id : RangeId
        The `RangeId` object returned by the `start_range` function.
    """
    libnvtx_end_range(range_id)


def enabled():
    """
    Returns True if nvtx is enabled.
    """
    return _ENABLED


if not enabled():

    class annotate(contextlib.nullcontext):
        def __init__(self, *args, **kwargs):
            super().__init__()

        def __call__(self, func):
            return func

    # Could use a decorator here but overheads are significant enough
    # not to. See https://github.com/NVIDIA/NVTX/pull/24 for discussion.
    def mark(message=None, color=None, domain=None, category=None, payload=None):
        pass

    def push_range(message=None, color=None, domain=None, category=None, payload=None):
        pass

    def pop_range(domain=None):
        pass

    def start_range(message=None, color=None, domain=None, category=None, payload=None):
        pass

    def end_range(range_id):
        pass
