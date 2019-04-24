/**
 * This file is part of the NoPoDoFo (R) project.
 * Copyright (c) 2017-2018
 * Authors: Cory Mickelson, et al.
 *
 * NoPoDoFo is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * NoPoDoFo is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

#include "Stream.h"
#include "../ErrorHandler.h"
#include "../ValidateArguments.h"
#include "Obj.h"
#include <spdlog/spdlog.h>

using namespace Napi;
using namespace PoDoFo;

using std::string;
using tl::nullopt;

namespace NoPoDoFo {

FunctionReference Stream::constructor; // NOLINT

Stream::Stream(const CallbackInfo& info)
  : ObjectWrap(info)
  , stream(info.Length() == 1 && info[0].IsExternal()
             ? *info[0].As<External<PdfStream>>().Data()
             : *Obj::Unwrap(info[0].As<Object>())->GetObject().GetStream())
{
  dbglog = spdlog::get("DbgLog");
}
Stream::~Stream()
{
  dbglog->debug("Stream Cleanup");
}
void
Stream::Initialize(Napi::Env& env, Napi::Object& target)
{
  HandleScope scope(env);
  Function ctor =
    DefineClass(env,
                "Stream",
                { InstanceMethod("write", &Stream::Write),
                  InstanceMethod("beginAppend", &Stream::BeginAppend),
                  InstanceMethod("append", &Stream::Append),
                  InstanceMethod("endAppend", &Stream::EndAppend),
                  InstanceMethod("inAppendMode", &Stream::IsAppending),
                  InstanceMethod("set", &Stream::Set),
                  InstanceMethod("copy", &Stream::GetCopy) });
  constructor = Napi::Persistent(ctor);
  constructor.SuppressDestruct();
  target.Set("Stream", ctor);
}

class StreamWriteAsync : public Napi::AsyncWorker
{
public:
  StreamWriteAsync(Napi::Function& cb, Stream* stream, string arg)
    : AsyncWorker(cb, "stream_write_async", stream->Value())
    , stream(stream)
    , arg(std::move(arg))
  {}

private:
  Stream* stream;
  PdfRefCountedBuffer buffer;
  PdfOutputDevice* device = nullptr;
  string arg;

  // AsyncWorker interface
protected:
  void Execute() override
  {
    try {
      if (!arg.empty()) {
        PdfOutputDevice fileDevice(arg.c_str());
        device = &fileDevice;
      } else {
        PdfOutputDevice memDevice(&buffer);
        device = &memDevice;
      }
      stream->GetStream().Write(device);
    } catch (PdfError& err) {
      SetError(String::New(Env(), ErrorHandler::WriteMsg(err)));
    }
  }
  void OnOK() override
  {
    if (arg.empty()) {
      Callback().Call(
        { Env().Null(),
          Buffer<char>::Copy(Env(), buffer.GetBuffer(), buffer.GetSize()) });
    }
    Callback().Call({ Env().Null(), String::New(Env(), arg) });
  }
};

Napi::Value
Stream::Write(const CallbackInfo& info)
{
  string output;
  Function cb;
  vector<int> opts =
    AssertCallbackInfo(info,
                       { { 0, { option(napi_function), option(napi_string) } },
                         { 1, { nullopt, option(napi_function) } } });
  if (opts[0] == 0) {
    cb = info[0].As<Function>();
  }
  if (opts[0] == 1) {
    output = info[0].As<String>();
  }
  if (opts[1] == 1) {
    cb = info[1].As<Function>();
  }
  StreamWriteAsync* worker = new StreamWriteAsync(cb, this, output);
  worker->Queue();
  return info.Env().Undefined();
}

void
Stream::BeginAppend(const Napi::CallbackInfo& info)
{
  std::vector<int> opt = AssertCallbackInfo(
    info,
    { { 0, { nullopt, option(napi_boolean), option(napi_external) } },
      { 1, { nullopt, option(napi_boolean) } },
      { 2, { nullopt, option(napi_boolean) } } });
  bool clearExisting = true;
  bool deleteFilter = true;
  std::vector<EPdfFilter>* filters = nullptr;
  if (opt[0] == 0) {
    GetStream().BeginAppend();
    return;
  } else if (opt[0] == 1 || opt[1] == 1) {
    clearExisting = info[0].As<Boolean>();
  } else if (opt[0] == 2) {
    filters = info[0].As<External<std::vector<EPdfFilter>>>().Data();
  }
  if (opt[2] == 1) {
    deleteFilter = info[2].As<Boolean>();
  }
  if (!filters) {
    GetStream().BeginAppend(clearExisting);
  } else {
    GetStream().BeginAppend(*filters, clearExisting, deleteFilter);
  }
}
void
Stream::Set(const Napi::CallbackInfo& info)
{
  if (info.Length() != 1 || (!info[0].IsString() && !info[0].IsBuffer())) {
    Error::New(info.Env(), "A string or buffer is required")
      .ThrowAsJavaScriptException();
    return;
  }
  if (info[0].IsBuffer()) {
    char* data = info[0].As<Buffer<char>>().Data();
    GetStream().Set(data);
  } else if (info[0].IsString()) {
    string data = info[0].As<String>().Utf8Value();
    GetStream().Set(data.c_str());
  }
}
void
Stream::Append(const Napi::CallbackInfo& info)
{
  if (info.Length() != 1 || (!info[0].IsString() && !info[0].IsBuffer())) {
    Error::New(info.Env(), "A string or buffer is required")
      .ThrowAsJavaScriptException();
    return;
  }

  try {
    if (info[0].IsBuffer()) {
      auto data = info[0].As<Buffer<char>>();
      GetStream().Append(data.Data(), data.Length());
    } else if (info[0].IsString()) {
      string data = info[0].As<String>().Utf8Value();
      GetStream().Append(data);
    }
  } catch (PdfError& err) {
    Error::New(info.Env(), err.what()).ThrowAsJavaScriptException();
  }
}
void
Stream::EndAppend(const Napi::CallbackInfo&)
{
  GetStream().EndAppend();
}
Napi::Value
Stream::IsAppending(const Napi::CallbackInfo& info)
{
  return Boolean::New(info.Env(), GetStream().IsAppending());
}
Napi::Value
Stream::Length(const Napi::CallbackInfo& info)
{
  return Number::New(info.Env(), GetStream().GetLength());
}
Napi::Value
Stream::GetCopy(const Napi::CallbackInfo& info)
{
  bool filtered = false;
  auto l = GetStream().GetLength();
  char* internalBuffer = static_cast<char*>(podofo_malloc(sizeof(char) * l));
  if (info.Length() == 1 && info[0].IsBoolean()) {
    filtered = info[0].As<Boolean>();
  }
  if (filtered) {
    GetStream().GetFilteredCopy(&internalBuffer, &l);
  } else {
    GetStream().GetCopy(&internalBuffer, &l);
  }
  auto output = Buffer<char>::Copy(info.Env(), internalBuffer, l);
  podofo_free(internalBuffer);
  return output;
}
}
