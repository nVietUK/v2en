import logging, os, contextlib, time, resource, librosa, numpy as np
import hashlib, soundfile as sf, platform, subprocess
from v2enlib import const
from tqdm import tqdm
from difflib import SequenceMatcher
from multiprocess.pool import ThreadPool
from multiprocess.context import TimeoutError as TLE


# debug utils
def functionTimeoutWrapper(s):
    def outer(fn):
        def inner(*args, **kwargs):
            with ThreadPool(processes=1) as pool:
                result = pool.apply_async(fn, args=args, kwds=kwargs)
                output = kwargs.get("default_value", None)
                with contextlib.suppress(TLE):
                    output = result.get(timeout=s) if s else result.get()
                return output

        return inner

    return outer


def functionTimeout(timeout, func, **kwargs):
    @functionTimeoutWrapper(timeout)
    def execute(func, **kwargs):
        args, kwargs = kwargs.get("args", None), kwargs.get("kwargs", None)
        return (
            func(*args, **kwargs)
            if args and kwargs
            else func(**kwargs)
            if kwargs
            else func(*args)
        )

    return execute(func, **kwargs)


def measureFunction(func):
    def wrapper(*args, **kwargs):
        start_time = time.monotonic()
        result = func(*args, **kwargs)
        end_time = time.monotonic()
        execution_time = end_time - start_time
        before = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        resource_consumption = before / 1024 / 1024  # Memory usage in MB
        if (
            execution_time < const.time_allow
            and resource_consumption < const.resource_allow
        ):
            return result

        logging.warn(
            f"{func.__name__}'s result:\n\tExecution time: {execution_time} seconds\n\tMemory consumption: {resource_consumption} MB"
        )
        return result

    return wrapper


def printError(text, error, important):
    text = f"{'_'*50}\n\tExpectation while {text}\n\tError type: {type(error)}\n\t{error}\n{chr(8254)*50}"
    logging.fatal(text)
    if important:
        print(text)


# terminal utils
def terminalWidth():
    try:
        return os.get_terminal_size().columns
    except Exception:
        return 0


def cleanScreen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


# sound utils
def playNotes(notes, durations, note_start_times):
    """
    Plays multiple notes simultaneously with varying durations and decreasing volume using a thread pool.
    """
    pool = ThreadPool(len(notes))
    for i in range(len(notes)):
        pool.apply_async(
            playNote,
            (
                notes[i],
                durations[i],
                1 - (i / len(notes)),
                durations[i],
                note_start_times[i],
            ),
        )
    pool.close()
    pool.join()


def playNote(note, duration, volume, note_duration, start_time):
    """
    Plays a single note with the given duration and volume using the soundfile library.
    """
    sr = 44100  # sample rate
    freq = librosa.note_to_hz(note)
    samples = scipy.signal.sawtooth(  # type: ignore
        2 * np.pi * np.arange(sr * note_duration) * freq / sr, 0.5
    )
    decay = np.linspace(volume, 0, int(sr * note_duration))
    scaled = samples * decay
    scaled /= np.max(np.abs(scaled))

    # Compute hash of audio data
    hashname = hashlib.sha256(scaled).hexdigest()

    # Create subdirectory for stored audio files
    os.makedirs(".wav", exist_ok=True)

    # Check if file with the same hash already exists
    filename = os.path.join(".wav", f"{hashname[:10]}.wav")
    if not os.path.exists(filename):
        # Write scaled audio data to file
        sf.write(filename, scaled, sr)

    time.sleep(start_time)

    # Play audio file using appropriate command depending on platform
    if platform.system() == "Windows":
        subprocess.Popen(
            [
                "powershell",
                'New-Object Media.SoundPlayer "{filename}"'.format(filename=filename),
            ]
        )
    elif platform.system() == "Darwin":
        subprocess.Popen(["afplay", filename])
    else:
        subprocess.Popen(["play", "-q", filename])


# other utils
def differentRatio(x, y):
    return SequenceMatcher(None, x, y).ratio()


def emptyFile(path):
    return os.stat(path).st_size == 0


def getKeyByValue(d, value):
    return [k for k, v in d.items() if v == value]


# thread utils
def functionPool(
    func,
    cmds,
    executor,
    isAllowThread=True,
    strictOrder=False,
    alwaysThread: bool = False,
    poolName: str = "",
) -> list:
    if (len(cmds)) == 0:
        return []
    with executor(
        processes=min(
            len(cmds), const.thread_limit if const.thread_limit > 0 else len(cmds)
        ),
    ) as ex:
        if (not const.thread_alow or not isAllowThread) and not alwaysThread:
            return [
                func(cmd)
                for cmd in tqdm(
                    cmds, leave=False, desc=poolName, disable=const.disableTQDM
                )
            ]
        with tqdm(
            total=len(cmds), leave=False, desc=poolName, disable=const.disableTQDM
        ) as pbar:
            results = []
            for res in (
                ex.imap(func, cmds) if strictOrder else ex.imap_unordered(func, cmds)
            ):
                pbar.update(1)
                results.append(res)
            return results


def argsPool(
    funcs: list,
    executor,
    subexecutor,
    isAllowThread: bool = True,
    strictOrder: bool = False,
    alwaysThread: bool = False,
    poolName: str = "",
    **kwargs,
) -> list:
    with executor(
        processes=min(
            len(funcs), const.thread_limit if const.thread_limit > 0 else len(funcs)
        ),
    ) as ex:
        if (not const.thread_alow or not isAllowThread) and not alwaysThread:
            return [
                subexecutor([func, kwargs])
                for func in tqdm(
                    funcs, leave=False, desc=poolName, disable=const.disableTQDM
                )
            ]
        with tqdm(
            total=len(funcs), leave=False, desc=poolName, disable=const.disableTQDM
        ) as pbar:
            results = []
            kwargsc = [dict(kwargs) for _ in range(len(funcs))]
            for res in (
                ex.imap(
                    subexecutor,
                    [[func, kwargsc[i]] for i, func in enumerate(funcs)],
                )
                if strictOrder
                else ex.imap_unordered(
                    subexecutor,
                    [[func, kwargsc[i]] for i, func in enumerate(funcs)],
                )
            ):
                pbar.update(1)
                results.append(res)
            return results


# logging init
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s\n%(message)s")
os.makedirs("logs", exist_ok=True)
os.makedirs(".wav", exist_ok=True)

file_handler = logging.FileHandler(f"./logs/{const.target}.log")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

logging.basicConfig(level=logging.DEBUG, handlers=[file_handler])
