# Systemtap Demo

Full System Observability for Linux

## Introduction

* Tracing script framework
  * Run scripts as kernel modules
  * Support User-space and Kernel tracing
  * Support Python and JVM

## Installation

[reference](https://wiki.ubuntu.com/Kernel/Systemtap)

## Syntax

* Systemtap is all about executing certain actions when hitting certain probes
* `probe <event> {handler}`

```c
probe timer.s(1)
{
    printf("hello world\n")
}
```

## Examples

### Callgraph (ls.stp)

Find function calls sequence for `/bin/ls`

```c
probe process("/bin/ls").function("*").call{
    log(thread_indent(1) . "=> " . probefunc() . " " .  $$parms)
}


probe process("/bin/ls").function("*").return{
    log(thread_indent(-1) . "<= " . probefunc() . " " .  $$return)
}
```

### System call (open.stp)

Find which process use `open` system call

```c
probe syscall.open {
    log(execname() . ": " . filename)
}
```

### Kenerl trace (iotop.stp, iotop2.stp)

`stap -l 'kernel.function("vfs_read")'`

```c
global reads, writes, total_io

probe vfs.read {
    reads[execname()] += $count
}

probe vfs.write {
    writes[execname()] += $count
}

probe timer.s(5) {
    printf("%16s\t%10s\t%10s\n", "Process", "KB Read", "KB Written")
    foreach (name in reads)
        total_io[name] += reads[name]
    foreach (name in writes)
        total_io[name] += writes[name]
    foreach (name in total_io- limit 10)
        printf("%16s\t%10d\t%10d\n", name, reads[name]/1024, writes[name]/1024)
    delete reads
    delete writes
    delete total_io
    printf("\n")
```

```c
global reads

probe vfs.read {
    reads[execname()] <<< $count
}
```

### Who sends SIGKILL (kill.stp)

If a process received `SIGKILL`, it dies imediately.
There is no chance for the process to log it.
However, we can use Systemtap to record the signal.

```c
probe signal.send {
  if (sig_name == "SIGKILL")
    printf("%s was sent to %s (pid:%d) by %s uid:%d\n",
           sig_name, pid_name, sig_pid, execname(), uid())
}
```

### Python (python.stp)

#### Build

[build instructions](https://docs.python.org/3/howto/instrumentation.html)

Build python with `./configure —with-dtrace`

#### Available marks

[link](https://docs.python.org/3/howto/instrumentation.html#available-static-markers)

* function_entry
* function_return
* line
* gc_start
* gc_done

```c
probe process("./Python-3.6.3/python").mark("function__entry") {
     filename = user_string($arg1);
     funcname = user_string($arg2);
     lineno = $arg3;

     printf("%s => %s in %s:%d\n",
            thread_indent(1), funcname, filename, lineno);
}

probe process("./Python-3.6.3/python").mark("function__return") {
    filename = user_string($arg1);
    funcname = user_string($arg2);
    lineno = $arg3;

    printf("%s <= %s in %s:%d\n",
           thread_indent(-1), funcname, filename, lineno);
}
```

#### FlameGraph for Python

[link](https://github.com/emfree/systemtap-python-tools)

### Dynamic Patch (keyhack.stp)

Systemtap can not only record the kernel behavior but also change it too.

This script will change the `event_code` everytime one press `m`
(this script must run in guru mode (`-g`))

`stap -l 'kernel.function(“kbd_event")'`

```c
probe kernel.function("kbd_event") {
  # Changes 'm' to 'b' .
  if ($event_code == 50) $event_code = 48
}

probe kernel.statement("*@/build/linux-8h04gD/linux-4.13.0/drivers/tty/vt/*.c:*"){
  log(pp())
}
```

## Other Features

### Embedded C functions

[link](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/5/html/systemtap_language_reference/ch03s06)

### Application markers

a.k.a. [User Space Probing To Apps](https://sourceware.org/systemtap/wiki/AddingUserSpaceProbingToApps)

### Tapset

`/usr/share/systemtap/tapset`

## Official Examples

[examples](https://sourceware.org/systemtap/examples/)

* callgraph
* lock
* socket
* IO
* strace/ltrace
* ...

## Conclusions

For Kernel/Userspace

* Tracing
* Profiling
* Debugging